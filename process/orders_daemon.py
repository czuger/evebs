#!/usr/bin/env python3
"""Daemon: continuously refresh public market orders.

Trade-hub regions are downloaded every pass. All regions (including non-hub)
are downloaded every 4th pass. Each pass runs the standard price updates.
If a pass finishes in under 15 minutes the daemon sleeps for the remainder.
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
from config import setup_logging, set_logger
setup_logging()
logger = set_logger('downloads')

# Route all esi.* module loggers (download modules use getLogger(__name__)) to
# downloads.log instead of the root evebs.log.
esi_logger = logging.getLogger('esi')
esi_logger.handlers = list(logger.handlers)
esi_logger.propagate = False

from app import app

MIN_LOOP_SECONDS = 60*15  # 15 minutes
NON_HUB_EVERY = 4 # Every hour


def _step(label, fn):
    t = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - t
    logger.info('  %s: %.1fs', label, elapsed)
    return result, elapsed


with app.app_context():
    from esi.download_public_orders.download import download as download_public_orders
    from process.update_jita_market_analytics import update_jita_market_analytics

    step = 0
    while True:
        step += 1
        region_scope = 'hub' if step % NON_HUB_EVERY != 0 else 'all'
        logger.info('=== Orders daemon step %d — regions=%s ===', step, region_scope)
        t_start = time.perf_counter()

        dl,  t_dl  = _step('download', lambda: download_public_orders(regions=region_scope))
        jma, t_jma = _step('jita_market_analytics', update_jita_market_analytics)

        elapsed = time.perf_counter() - t_start
        logger.info('=== Step %d done in %.1fs ===', step, elapsed)

        logger.info('=== Step %d summary ===', step)
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
            logger.info('  JMA update (%.1fs): %d rows, %d with price_forecast_3d',
                        t_jma, jma['rows'], jma['with_forecast'])
        logger.info('  Total step time: %.1fs', elapsed)

        sleep_for = MIN_LOOP_SECONDS - elapsed
        if sleep_for > 0:
            logger.info('Sleeping %.1fs to reach %dm cadence...', sleep_for, MIN_LOOP_SECONDS // 60)
            time.sleep(sleep_for)
