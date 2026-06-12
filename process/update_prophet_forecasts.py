#!/usr/bin/env python3
"""Prophet upgrade for the >=90-day tier of jita_price_forecasts.

Runs the fast SQL baseline (process/update_price_forecasts.py — linear / min_price), then
fits Facebook Prophet on the daily Jita (The Forge, region 10000002) `average` series of
every item with >=90 days of history and overwrites those rows with method='prophet'.
Prophet is more robust than the linear regression on illiquid/noisy series. Fits run
serially (one item at a time); progress + ETA are logged every 100 items.
"""
import argparse
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from prophet import Prophet
from sqlalchemy import text

from config import set_logger
from evebs import create_db_app
from evebs.extensions import db
from process.update_price_forecasts import update_price_forecasts, FORGE_REGION_ID

# Prophet/cmdstanpy log one+ INFO line per fit (24k+ for a full run) — silence them.
logging.getLogger('cmdstanpy').disabled = True
logging.getLogger('prophet').setLevel(logging.CRITICAL)

logger = set_logger('update_prophet_forecasts')

_MIN_DAYS = 90       # tier threshold: items with >= this many days of data use Prophet
_TRAIN_DAYS = 365    # history window fed to Prophet
_UPSERT_CHUNK = 1000


def _fit_prophet(ds_list, y_list):
    """Fit Prophet on one item's daily average series → +3-day yhat (clamped >= 0).

    Returns None on a fit failure so one bad series never aborts the batch.
    """
    try:
        df = pd.DataFrame({'ds': pd.to_datetime(ds_list), 'y': y_list})
        model = Prophet(weekly_seasonality=True, yearly_seasonality=False,
                        daily_seasonality=False)
        model.fit(df)
        future = model.make_future_dataframe(periods=3)
        yhat = float(model.predict(future)['yhat'].iloc[-1])
        return max(yhat, 0.0)
    except (ValueError, RuntimeError):
        return None


def _load_eligible_series(train_days, min_days):
    """Per-item (type_id, dates, averages) for Forge items with >= min_days of history."""
    cutoff = f"CURRENT_DATE - INTERVAL '{int(train_days)} days'"
    result = db.session.execute(
        text(f"""
            SELECT type_id, date, average
            FROM market_histories
            WHERE region_id = :rid AND date >= {cutoff} AND average IS NOT NULL
              AND type_id IN (
                  SELECT type_id FROM market_histories
                  WHERE region_id = :rid AND date >= {cutoff} AND average IS NOT NULL
                  GROUP BY type_id HAVING COUNT(DISTINCT date) >= :min_days
              )
            ORDER BY type_id, date
        """),
        {'rid': FORGE_REGION_ID, 'min_days': min_days},
    ).yield_per(50_000)

    series = {}
    for type_id, d, avg in result:
        ds, ys = series.setdefault(type_id, ([], []))
        ds.append(d)
        ys.append(avg)
    return [(tid, ds, ys) for tid, (ds, ys) in series.items()]


def _upsert_prophet(results):
    if not results:
        return
    stmt = text("""
        INSERT INTO jita_price_forecasts (id, price_forecast_3d, method, updated_at)
        VALUES (:id, :f, 'prophet', now())
        ON CONFLICT (id) DO UPDATE SET
            price_forecast_3d = EXCLUDED.price_forecast_3d,
            method            = 'prophet',
            updated_at        = now()
    """)
    items = list(results.items())
    for i in range(0, len(items), _UPSERT_CHUNK):
        db.session.execute(stmt, [{'id': tid, 'f': val} for tid, val in items[i:i + _UPSERT_CHUNK]])
    db.session.commit()


def _fmt_duration(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f'{h}h{m:02d}m{s:02d}s'
    if m:
        return f'{m}m{s:02d}s'
    return f'{s}s'


def _log_progress(done, total, fitted, start):
    elapsed = time.perf_counter() - start
    rate = done / elapsed if elapsed > 0 else 0.0
    eta = (total - done) / rate if rate > 0 else 0.0
    logger.info('prophet: %d/%d items (%d fitted) — %.1f/s, elapsed %s, ETA %s',
                done, total, fitted, rate, _fmt_duration(elapsed), _fmt_duration(eta))


def update_prophet_forecasts(train_days=_TRAIN_DAYS, min_days=_MIN_DAYS,
                             forecaster=None, run_baseline=True):
    """Refresh the baseline, then overwrite >= min_days items with Prophet forecasts.

    forecaster: optional injected `f(ds_list, y_list) -> float|None` (used by tests) in
    place of the real Prophet fit. Fits run serially; progress is logged every 100 items.
    Returns {'eligible', 'fitted', 'failed', 'counts'}.
    """
    if run_baseline:
        update_price_forecasts()

    series = _load_eligible_series(train_days, min_days)
    eligible = len(series)
    logger.info('prophet: %d eligible items (>= %d days)', eligible, min_days)

    fit = forecaster or _fit_prophet
    results = {}
    start = time.perf_counter()
    for done, (type_id, ds, ys) in enumerate(series, 1):
        val = fit(ds, ys)
        if val is not None:
            results[type_id] = val
        if done % 100 == 0 or done == eligible:
            _log_progress(done, eligible, len(results), start)

    fitted = len(results)
    _upsert_prophet(results)

    counts = dict(db.session.execute(
        text('SELECT method, COUNT(*) FROM jita_price_forecasts GROUP BY method')
    ).all())
    logger.info('prophet forecasts: %d fitted, %d failed | method split: %s',
                fitted, eligible - fitted, counts)
    return {'eligible': eligible, 'fitted': fitted, 'failed': eligible - fitted, 'counts': counts}


def main():
    parser = argparse.ArgumentParser(
        description='Fit Prophet for the >=90-day tier of jita_price_forecasts.')
    parser.add_argument('--skip-baseline', action='store_true',
                        help='Do not recompute the SQL baseline first.')
    parser.add_argument('-n', '--no-op', action='store_true',
                        help='Dry-run: print current prophet row count, do not fit.')
    args = parser.parse_args()

    with create_db_app().app_context():
        if args.no_op:
            count = db.session.execute(
                text("SELECT COUNT(*) FROM jita_price_forecasts WHERE method = 'prophet'")
            ).scalar()
            logger.info('Dry-run — %d prophet rows currently.', count)
            sys.exit(0)
        update_prophet_forecasts(run_baseline=not args.skip_baseline)


if __name__ == '__main__':
    main()
