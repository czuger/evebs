#!/usr/bin/env python3
"""Precompute per-item Prophet parameters into eve_items.prophet_parameters.

For each item traded in The Forge (region 10000002), this analyses its market_histories
price series, derives item-tuned Prophet hyper-parameters + a runtime config, and stores
the result as JSON on EveItem.prophet_parameters. process/refresh_market_forecast.py then
fits Prophet per item using these stored params. See the EveItem.prophet_parameters comment
for the exact JSON shape.

No Flask app/context: drives the DB through a standalone SQLAlchemy session.
"""
import argparse
import os
import sys
from datetime import UTC, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from scipy.stats import linregress
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import Config, set_logger
from evebs.models import EveItem, MarketHistory

logger = set_logger('compute_prophet_params')

FORGE_REGION_ID = 10000002
MIN_DAYS = 30            # below this → status='insufficient_data', no params
BATCH_SIZE = 500         # bulk_update_mappings flush size
PROGRESS_EVERY = 100

# Volatility cut-offs (std of daily pct-change) → changepoint_prior_scale tiers.
VOL_LOW = 0.05           # < VOL_LOW  → 0.05 (stable)
VOL_HIGH = 0.15          # < VOL_HIGH → 0.10 (medium); else 0.30 (volatile)


def _reliability_score(data_days, missing_ratio, volatility, outlier_ratio, trend_strength):
    """0-100 composite: data coverage (40) + price stability (30) + cleanliness (20) +
    trend clarity (10). Higher = more trustworthy history. Tunable."""
    coverage = min(data_days, 365) / 365.0 * (1.0 - missing_ratio) * 40.0
    stability = max(0.0, 1.0 - (volatility or 0.0) / 0.30) * 30.0
    cleanliness = max(0.0, 1.0 - (outlier_ratio or 0.0)) * 20.0
    clarity = max(0.0, min(1.0, trend_strength or 0.0)) * 10.0
    return float(max(0.0, min(100.0, coverage + stability + cleanliness + clarity)))


def _finite(value, default=0.0):
    """Coerce NaN/inf (which Postgres JSON rejects) to a finite default."""
    value = float(value)
    return value if np.isfinite(value) else default


def _data_summary(dates, prices, volumes):
    """Compute the data_summary metrics from one item's daily price/volume history."""
    data_days = len(prices)
    span_days = (dates[-1] - dates[0]).days + 1
    missing_ratio = float(max(0.0, (span_days - data_days) / span_days)) if span_days else 0.0

    series = pd.Series(prices, dtype='float64')
    volatility = _finite(series.pct_change().std())       # NaN for a 1-row / constant series

    x = np.arange(data_days, dtype='float64')
    reg = linregress(x, prices)
    # linregress returns rvalue=NaN for a zero-variance (flat) price series.
    trend_strength = _finite(reg.rvalue ** 2)             # abs R² (always >= 0)
    trend_direction = 'up' if (np.isfinite(reg.slope) and reg.slope > 0) else 'down'

    pmin, pmax = float(np.min(prices)), float(np.max(prices))
    price_range_ratio = _finite(pmax / pmin, 1.0) if pmin > 0 else 1.0

    q1, q3 = np.percentile(prices, [25, 75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outlier_ratio = float(np.mean((prices < lo) | (prices > hi)))

    return {
        'data_days': data_days,
        'missing_ratio': _finite(missing_ratio),
        'avg_price': _finite(np.mean(prices)),
        'avg_volume': _finite(np.mean(volumes)) if len(volumes) else 0.0,
        'volatility': volatility,
        'trend_strength': trend_strength,
        'trend_direction': trend_direction,
        'price_range_ratio': price_range_ratio,
        'outlier_ratio': _finite(outlier_ratio),
        'reliability_score': _finite(_reliability_score(
            data_days, missing_ratio, volatility, outlier_ratio, trend_strength)),
    }


def _derive_params(summary):
    """Map a data_summary into (prophet_params, runtime_config)."""
    data_days = summary['data_days']
    volatility = summary['volatility']
    range_ratio = summary['price_range_ratio']
    reliability = summary['reliability_score']

    multiplicative = range_ratio > 3
    if volatility < VOL_LOW:
        changepoint_prior_scale = 0.05
    elif volatility < VOL_HIGH:
        changepoint_prior_scale = 0.1
    else:
        changepoint_prior_scale = 0.3

    n_changepoints = 15 if data_days < 180 else (30 if data_days < 365 else 50)

    prophet_params = {
        'changepoint_prior_scale': changepoint_prior_scale,
        'seasonality_prior_scale': 15 if multiplicative else 5,
        'seasonality_mode': 'multiplicative' if multiplicative else 'additive',
        'n_changepoints': n_changepoints,
        'changepoint_range': 0.8 if summary['missing_ratio'] > 0.1 else 0.9,
        'yearly_seasonality': data_days > 365,
        'weekly_seasonality': True,
        'interval_width': 0.80,
    }
    runtime_config = {
        'log_transform': range_ratio > 5,
        'forecast_days': 7 if reliability < 50 else (14 if reliability < 75 else 30),
    }
    return prophet_params, runtime_config


def compute_prophet_params(region_id=FORGE_REGION_ID, limit=None, session=None, logger=logger):
    """Compute prophet_parameters for every eve_item with Forge market history.
    Returns a status→count dict."""
    existing_ids = {i for (i,) in session.query(EveItem.id)}
    type_ids = [t for (t,) in session.query(MarketHistory.type_id)
                .filter(MarketHistory.region_id == region_id).distinct()
                if t in existing_ids]
    if limit:
        type_ids = type_ids[:limit]
    total = len(type_ids)
    logger.info('compute_prophet_params: %d items with Forge history', total)

    counts = {}
    batch = []
    for done, type_id in enumerate(type_ids, 1):
        rows = (session.query(MarketHistory.date, MarketHistory.average, MarketHistory.volume)
                .filter_by(region_id=region_id, type_id=type_id)
                .order_by(MarketHistory.date.asc()).all())
        rows = [r for r in rows if r.average is not None and r.average > 0]
        computed_at = datetime.now(UTC).isoformat()

        if len(rows) < MIN_DAYS:
            payload = {'status': 'insufficient_data', 'computed_at': computed_at,
                       'data_days': len(rows)}
            counts['insufficient_data'] = counts.get('insufficient_data', 0) + 1
        else:
            dates = [r.date for r in rows]
            prices = np.array([float(r.average) for r in rows], dtype='float64')
            volumes = np.array([float(r.volume or 0) for r in rows], dtype='float64')
            summary = _data_summary(dates, prices, volumes)
            prophet_params, runtime_config = _derive_params(summary)
            payload = {'status': 'ok', 'computed_at': computed_at,
                       'data_summary': summary, 'prophet_params': prophet_params,
                       'runtime_config': runtime_config}
            counts['ok'] = counts.get('ok', 0) + 1

        batch.append({'id': type_id, 'prophet_parameters': payload})
        if len(batch) >= BATCH_SIZE:
            session.bulk_update_mappings(EveItem, batch)
            session.commit()
            batch = []
        if done % PROGRESS_EVERY == 0 or done == total:
            logger.info('compute_prophet_params: %d/%d items — %s', done, total, counts)

    if batch:
        session.bulk_update_mappings(EveItem, batch)
        session.commit()
    logger.info('compute_prophet_params: done — %s', counts)
    return counts


def main():
    parser = argparse.ArgumentParser(
        description='Precompute per-item Prophet parameters into eve_items.prophet_parameters.')
    parser.add_argument('-r', '--region', type=int, default=FORGE_REGION_ID,
                        help=f'Region id to analyse (default: The Forge {FORGE_REGION_ID}).')
    parser.add_argument('-l', '--limit', type=int, default=None,
                        help='Only process the first N items (for testing).')
    args = parser.parse_args()

    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    with Session(engine) as session:
        compute_prophet_params(region_id=args.region, limit=args.limit, session=session)


if __name__ == '__main__':
    main()
