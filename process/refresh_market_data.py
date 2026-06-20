#!/usr/bin/env python3
"""One-shot market-data refresh: download public orders, then run the price/cost updates.

Runs a single pass and exits — it is no longer a daemon. Fired periodically by cron via
`docker start app-eve-public-orders`; a Redis lock makes overlapping runs safe (a run still in progress is skipped)
and a Redis run-counter preserves the old cadence: trade-hub regions every run, all regions
every 4th run.

No Flask application context: the DB call-chain is driven by a standalone SQLAlchemy
Session passed explicitly into each download/update function (they default to the
Flask-scoped db.session for the web app / other scripts, but here we never build a Flask app).
"""
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import redis as redis_lib
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import Config, set_logger
from esi.download_public_orders.download import download as download_public_orders
from process.update_blueprints import refresh_blueprint_manufacturing_costs
from process.update_jita_min_prices import update_jita_min_prices
from process.update_price_forecasts import refresh_forecast_mvs

logger = set_logger('downloads')

# Route esi.* and process.* module loggers (they use getLogger(__name__)) to downloads.log
# instead of the unconfigured root logger.
for _name in ('esi', 'process'):
    _lg = logging.getLogger(_name)
    _lg.handlers = list(logger.handlers)
    _lg.propagate = False

NON_HUB_EVERY = 4                 # all regions every 4th run, hub-only otherwise
LOCK_KEY = 'refresh_market_data:lock'
RUN_COUNT_KEY = 'refresh_market_data:run_count'
LOCK_TTL = 60 * 60                # > worst-case run; auto-frees the lock if a run crashes


def _step(label, fn):
    t = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - t
    logger.info('  %s: %.1fs', label, elapsed)
    return result, elapsed


def _run(session, region_scope):
    logger.info('=== Market refresh — regions=%s ===', region_scope)
    t_start = time.perf_counter()

    dl,  t_dl  = _step('download', lambda: download_public_orders(regions=region_scope, session=session))
    jma, t_jma = _step('jita_min_prices', lambda: update_jita_min_prices(session=session))
    bpc, t_bpc = _step('blueprint_costs', lambda: refresh_blueprint_manufacturing_costs(session=session))
    fmv, t_fmv = _step('forecast_mvs', lambda: refresh_forecast_mvs(session=session))

    elapsed = time.perf_counter() - t_start
    logger.info('=== Refresh done in %.1fs ===', elapsed)

    logger.info('=== Summary ===')
    if dl:
        logger.info('  Download (%.1fs):', t_dl)
        for r in dl['per_region']:
            logger.info('    %-30s  +%d new  ~%d updated  =%d unchanged  (%d pending)',
                        r['name'], r['created'], r['updated'], r['touched'], r['pending'])
        logger.info('    Total:  +%d created  ~%d updated  =%d unchanged  -%d deleted',
                    dl['created'], dl['updated'], dl['touched'], dl['deleted'])
        logger.info('    Sales recorded: %d  |  Skipped: %d no-hub  %d zero-volume',
                    dl['sales_created'], dl['skipped_no_hub'], dl['skipped_zero'])
    if jma:
        logger.info('  Jita min prices refresh (%.1fs): %d rows', t_jma, jma['rows'])
    if bpc:
        logger.info('  Blueprint costs (%.1fs): %d updated, %d no price',
                    t_bpc, bpc['updated'], bpc['no_price'])
    if fmv:
        logger.info('  Forecast MVs (%.1fs): price %d items, volume %d items',
                    t_fmv, fmv['price_items'], fmv['vol_items'])
    logger.info('  Total time: %.1fs', elapsed)


def main():
    r = redis_lib.from_url(Config.REDIS_URL)
    lock = r.lock(LOCK_KEY, timeout=LOCK_TTL, blocking=False)
    if not lock.acquire():
        logger.info('Another market refresh is already running — skipping this run.')
        return

    try:
        region_scope = 'all' if r.incr(RUN_COUNT_KEY) % NON_HUB_EVERY == 0 else 'hub'
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        with Session(engine) as session:
            _run(session, region_scope)
    finally:
        try:
            lock.release()
        except redis_lib.exceptions.LockError:
            # Lock TTL expired mid-run (run took longer than LOCK_TTL); nothing to release.
            pass


if __name__ == '__main__':
    main()
