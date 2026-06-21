"""Prophet-based 5-day market forecast for a (region, type).

`generate_forecast` fits Facebook Prophet on a (region, type)'s daily `average`,
`lowest` and `volume` series from `market_histories` and stores the next 5 days of
predictions (with confidence bands) in `market_prophet_forecasts`. Only prophet-ready items
are forecast: the Prophet model is built from the item's precomputed
`EveItem.prophet_parameters` (see process/compute_prophet_params.py), with an optional log
transform from runtime_config. The Prophet fit is injectable via `forecaster` so callers/tests
can supply a deterministic stand-in without running Prophet.
"""
import argparse
import logging
import os
import sys
import time
from datetime import UTC, date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from prophet import Prophet
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import Config, set_logger
from esi.download_market_histories import download_market_histories
from evebs.extensions import db
from evebs.models import (
    EveItem, MarketHistory, MarketProphetForecast, MarketProphetForecastErrors,
)

# Prophet / cmdstanpy log one+ INFO line per fit — keep them quiet for callers.
logging.getLogger('prophet').setLevel(logging.WARNING)
logging.getLogger('cmdstanpy').disabled = True

FORECAST_DAYS = 5
MIN_ROWS = 30
FORGE_REGION_ID = 10000002   # The Forge (Jita)
CONFIDENCE = 0.95            # the only confidence level computed


def _price_direction(last_price, avg_predicted):
    """Encode the predicted average vs the last market price: flat=0, up=1, slow_up=2,
    down=-1, slow_down=-2, None when not computable."""
    if last_price is None or avg_predicted is None or avg_predicted <= 0:
        return None
    if avg_predicted > last_price * 1.05:
        return 1
    if avg_predicted > last_price * 1.001:
        return 2
    if avg_predicted < last_price * 0.95:
        return -1
    if avg_predicted < last_price * 0.999:
        return -2
    return 0


def _prophet_fit(ds_list, y_list, periods, params, log_transform=False):
    """Fit Prophet with the item's stored `params` and return `periods` future
    (yhat, yhat_lower, yhat_upper) tuples. When `log_transform` is set, the series is fit in
    log1p space and the predictions are inverted with expm1."""
    y = np.log1p(y_list) if log_transform else y_list
    df = pd.DataFrame({'ds': pd.to_datetime(ds_list), 'y': y})
    model = Prophet(
        changepoint_prior_scale=params['changepoint_prior_scale'],
        seasonality_prior_scale=params['seasonality_prior_scale'],
        seasonality_mode=params['seasonality_mode'],
        n_changepoints=params['n_changepoints'],
        changepoint_range=params['changepoint_range'],
        yearly_seasonality=params['yearly_seasonality'],
        weekly_seasonality=params['weekly_seasonality'],
        interval_width=params['interval_width'],
    )
    model.fit(df)
    future = model.make_future_dataframe(periods=periods)
    pred = model.predict(future).tail(periods)
    out = list(zip(pred['yhat'], pred['yhat_lower'], pred['yhat_upper']))
    if log_transform:
        out = [(float(np.expm1(a)), float(np.expm1(b)), float(np.expm1(c))) for a, b, c in out]
    return out


def _clear_existing(region_id, type_id, confidence, session):
    """Drop any prior forecast rows and error marker for this (region, type)."""
    session.query(MarketProphetForecast).filter_by(
        region_id=region_id, type_id=type_id).delete()
    session.query(MarketProphetForecastErrors).filter_by(
        region_id=region_id, type_id=type_id, confidence=confidence).delete()


def _store_error(region_id, type_id, confidence, reason, session):
    """Replace this (region, type, confidence)'s forecast with a single error row."""
    _clear_existing(region_id, type_id, confidence, session)
    session.add(MarketProphetForecastErrors(
        region_id=region_id, type_id=type_id, confidence=confidence, reason=reason))
    session.commit()
    return {"status": "error", "reason": reason}


def generate_forecast(region_id, type_id, confidence=CONFIDENCE, forecaster=None, session=None):
    """Generate and persist a 5-day Prophet forecast for one (region, type, confidence).

    Every stored row is fully populated; anything that would yield a null is recorded in
    MarketProphetForecastErrors instead (returning {"status": "error", "reason": …}).
    On success stores 5 rows and returns {"status": "ok", "inserted": 5}. `forecaster`
    overrides the Prophet fit.
    """
    session = session or db.session
    fit = forecaster or _prophet_fit

    item = session.get(EveItem, type_id)
    if item is None or not item.prophet_ready:
        return _store_error(region_id, type_id, confidence, 'not_prophet_ready', session)
    params = item.prophet_params
    log_transform = item.prophet_runtime.get('log_transform', False)

    rows = (session.query(MarketHistory)
            .filter_by(region_id=region_id, type_id=type_id)
            .order_by(MarketHistory.date.asc())
            .all())
    rows = [r for r in rows
            if (r.average or 0) > 0 and (r.lowest or 0) > 0
            and (r.highest or 0) > 0 and (r.volume or 0) > 0]
    if len(rows) < MIN_ROWS:
        return _store_error(region_id, type_id, confidence, 'not_enough_history', session)

    # Volume must be forecastable (no null vol fields allowed).
    zero_vol_ratio = sum(1 for r in rows if (r.volume or 0) == 0) / len(rows)
    if zero_vol_ratio > 0.5:
        return _store_error(region_id, type_id, confidence, 'unreliable_volume', session)

    ds = [r.date for r in rows]
    last_date = rows[-1].date
    last_price = rows[-1].average   # most recent valid market-history average price
    forecast_dates = [last_date + timedelta(days=i) for i in range(1, FORECAST_DAYS + 1)]

    avg = fit(ds, [r.average for r in rows], FORECAST_DAYS, params, log_transform)
    low = fit(ds, [r.lowest for r in rows], FORECAST_DAYS, params, log_transform)
    high = fit(ds, [r.highest for r in rows], FORECAST_DAYS, params, log_transform)
    vol = fit(ds, [r.volume for r in rows], FORECAST_DAYS, params, log_transform)

    generated_at = datetime.now(UTC)
    new_rows = []
    for i, fc_date in enumerate(forecast_dates):
        avg_p = float(avg[i][0])
        vol_p = float(round(vol[i][0]))
        if avg_p == 0 or vol_p == 0:   # would make a *_spread_pct null
            return _store_error(region_id, type_id, confidence, 'zero_division', session)
        low_p, high_p = float(low[i][0]), float(high[i][0])
        vol_lo, vol_hi = float(round(vol[i][1])), float(round(vol[i][2]))
        price_spread = high_p - low_p
        new_rows.append(MarketProphetForecast(
            region_id=region_id, type_id=type_id, forecast_date=fc_date,
            generated_at=generated_at, confidence=confidence,
            avg_predicted=avg_p, avg_lower=float(avg[i][1]), avg_upper=float(avg[i][2]),
            low_predicted=low_p, low_lower=float(low[i][1]), low_upper=float(low[i][2]),
            high_predicted=high_p, high_lower=float(high[i][1]), high_upper=float(high[i][2]),
            vol_predicted=vol_p, vol_lower=vol_lo, vol_upper=vol_hi,
            price_spread=price_spread, price_spread_pct=price_spread / avg_p,
            price_direction=_price_direction(last_price, avg_p),
        ))

    _clear_existing(region_id, type_id, confidence, session)
    session.bulk_save_objects(new_rows)
    session.commit()
    return {"status": "ok", "inserted": len(new_rows)}


def recompute_price_directions(region_id=FORGE_REGION_ID, logger=None, session=None):
    """Recompute price_direction on existing forecasts (no Prophet): per item, compare each
    row's avg_predicted to the most recent market_history average. Returns rows updated."""
    session = session or db.session
    type_ids = [t for (t,) in session.query(MarketProphetForecast.type_id)
                .filter_by(region_id=region_id).distinct()]
    updated = 0
    for type_id in type_ids:
        last = (session.query(MarketHistory)
                .filter_by(region_id=region_id, type_id=type_id)
                .order_by(MarketHistory.date.desc()).first())
        last_price = last.average if last else None
        for row in (session.query(MarketProphetForecast)
                    .filter_by(region_id=region_id, type_id=type_id).all()):
            row.price_direction = _price_direction(last_price, row.avg_predicted)
            updated += 1
    session.commit()
    if logger:
        logger.info('market_forecast: recomputed price_direction for %d rows (%d items)',
                    updated, len(type_ids))
    return updated


def _fmt_duration(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f'{h}h{m:02d}m{s:02d}s'
    if m:
        return f'{m}m{s:02d}s'
    return f'{s}s'


def run_all(region_id=FORGE_REGION_ID, confidence=CONFIDENCE, forecaster=None,
            limit=None, logger=None, session=None):
    """Generate forecasts for every prophet-ready EveItem (prophet_parameters.status == 'ok').
    Returns a status→count dict. A single item's Prophet failure is logged and skipped, not
    fatal to the batch. Logs progress with rate + ETA every 100 items (and on the final item)."""
    session = session or db.session
    item_ids = [i for (i,) in session.query(EveItem.id)
                .filter(EveItem.prophet_parameters['status'].astext == 'ok')]
    if limit:
        item_ids = item_ids[:limit]
    total = len(item_ids)
    counts = {}
    start = time.perf_counter()
    for done, type_id in enumerate(item_ids, 1):
        try:
            result = generate_forecast(region_id, type_id, confidence=confidence,
                                       forecaster=forecaster, session=session)
            key = result.get('status', 'error')
        except (ValueError, RuntimeError) as exc:
            session.rollback()
            key = 'failed'
            if logger:
                logger.warning('market_forecast: item %s failed: %s', type_id, exc)
        counts[key] = counts.get(key, 0) + 1
        if logger and (done % 100 == 0 or done == total):
            elapsed = time.perf_counter() - start
            rate = done / elapsed if elapsed > 0 else 0.0
            eta = (total - done) / rate if rate > 0 else 0.0
            logger.info('market_forecast: %d/%d items — %.1f/s, elapsed %s, ETA %s — %s',
                        done, total, rate, _fmt_duration(elapsed), _fmt_duration(eta), counts)
    return counts


def main():
    parser = argparse.ArgumentParser(
        description='Generate Prophet market forecasts for all EveItems.')
    parser.add_argument('-r', '--region', type=int, default=FORGE_REGION_ID,
                        help=f'Region id to forecast (default: The Forge {FORGE_REGION_ID}).')
    parser.add_argument('-l', '--limit', type=int, default=None,
                        help='Only process the first N items (for testing).')
    parser.add_argument('-p', '--price-direction-only', action='store_true',
                        help='Recompute only price_direction on existing forecasts (no Prophet).')
    parser.add_argument('-d', '--download-histories', action='store_true',
                        help='First download fresh market histories from ESI, then forecast.')
    args = parser.parse_args()

    logger = set_logger('market_forecast')
    # No Flask app/context: drive the DB through a standalone SQLAlchemy session.
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    with Session(engine) as session:
        if args.download_histories:
            logger.info('market_forecast: downloading market histories first...')
            result = download_market_histories(
                forge_only=(args.region == FORGE_REGION_ID), session=session)
            logger.info('market_forecast: histories downloaded — %s', result)

        if args.price_direction_only:
            recompute_price_directions(args.region, logger=logger, session=session)
        else:
            counts = run_all(args.region, limit=args.limit, logger=logger, session=session)
            logger.info('market_forecast: done — %s', counts)


if __name__ == '__main__':
    main()
