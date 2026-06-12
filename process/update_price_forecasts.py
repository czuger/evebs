#!/usr/bin/env python3
"""Recompute the jita_price_forecasts table — a 3-day price forecast per item type.

Source: market_histories for The Forge (region 10000002), last 90 days of daily `average`.
Tiered by how many days of data an item has:
  - >= 14 days : volume-weighted linear regression (SQL), evaluated at CURRENT_DATE + 3.
  - <  14 days : fall back to the current jita_min_prices.min_sell_price.
The >= 90-day tier is upgraded to Prophet by process/update_prophet_forecasts.py, which
runs this baseline first and then overwrites those rows with method='prophet'.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from config import set_logger
from evebs import create_db_app
from evebs.extensions import db

logger = set_logger('update_price_forecasts')

FORGE_REGION_ID = 10000002

# Volume-weighted linear regression of daily `average` over the last 90 days, evaluated at
# CURRENT_DATE + 3, falling back to jita_min_prices for items with < 14 days of data.
_SQL = """
INSERT INTO jita_price_forecasts (id, price_forecast_3d, method, updated_at)
WITH
daily AS (
    SELECT
        type_id                            AS eve_item_id,
        EXTRACT(EPOCH FROM date) / 86400.0 AS x,
        average                            AS y,
        volume::float                      AS w
    FROM market_histories
    WHERE region_id = :forge_region_id
      AND date >= CURRENT_DATE - INTERVAL '90 days'
      AND average IS NOT NULL
),
agg AS (
    SELECT
        eve_item_id,
        COUNT(*)     AS n_days,
        SUM(w)       AS sw,
        SUM(w * x)   AS swx,
        SUM(w * y)   AS swy,
        SUM(w * x*x) AS swxx,
        SUM(w * x*y) AS swxy
    FROM daily
    GROUP BY eve_item_id
),
linear AS (
    SELECT
        eve_item_id,
        CASE WHEN n_days >= 14 AND sw > 0 AND (sw * swxx - swx * swx) <> 0
             THEN swy / sw
                  + ((sw * swxy - swx * swy) / (sw * swxx - swx * swx))
                    * (EXTRACT(EPOCH FROM CURRENT_DATE) / 86400.0 + 3 - swx / sw)
        END AS lin_forecast
    FROM agg
)
SELECT
    COALESCE(l.eve_item_id, j.id)                                            AS id,
    COALESCE(l.lin_forecast, j.min_sell_price)                              AS price_forecast_3d,
    CASE WHEN l.lin_forecast IS NOT NULL THEN 'linear' ELSE 'min_price' END AS method,
    now()
FROM linear l
FULL OUTER JOIN jita_min_prices j ON j.id = l.eve_item_id
WHERE COALESCE(l.lin_forecast, j.min_sell_price) IS NOT NULL
"""


def refresh_forecast_mvs():
    """Refresh the dual-window (7d + 30d) linear-regression forecast MVs (price + volume,
    non-concurrent) from sales_finals. Returns the per-MV item counts. Cheap enough to run
    every orders-daemon pass; does NOT touch the jita_price_forecasts table or Prophet rows."""
    db.session.execute(text('REFRESH MATERIALIZED VIEW jita_price_forecast_linear_regression'))
    db.session.execute(text('REFRESH MATERIALIZED VIEW jita_volume_forecast_linear_regression'))
    db.session.commit()

    price_items = db.session.execute(
        text('SELECT COUNT(DISTINCT type_id) FROM jita_price_forecast_linear_regression')).scalar()
    vol_items = db.session.execute(
        text('SELECT COUNT(DISTINCT type_id) FROM jita_volume_forecast_linear_regression')).scalar()
    logger.info('forecast MVs refreshed: price %d items, volume %d items.', price_items, vol_items)
    return {'price_items': price_items, 'vol_items': vol_items}


def update_price_forecasts():
    """Recompute the jita_price_forecasts table and refresh the forecast materialized views.
    Returns counts."""
    db.session.execute(text('DELETE FROM jita_price_forecasts'))
    db.session.execute(text(_SQL), {'forge_region_id': FORGE_REGION_ID})
    db.session.commit()

    mvs = refresh_forecast_mvs()

    counts = dict(db.session.execute(
        text('SELECT method, COUNT(*) FROM jita_price_forecasts GROUP BY method')
    ).all())
    linear = counts.get('linear', 0)
    min_price = counts.get('min_price', 0)
    total = linear + min_price
    logger.info('jita_price_forecasts updated: %d rows (%d linear, %d min_price).',
                total, linear, min_price)
    return {'rows': total, 'linear': linear, 'min_price': min_price,
            'price_items': mvs['price_items'], 'vol_items': mvs['vol_items']}


def main():
    parser = argparse.ArgumentParser(description='Recompute the jita_price_forecasts table.')
    parser.add_argument('-n', '--no-op', action='store_true',
                        help='Dry-run: print current row count, do not recompute.')
    args = parser.parse_args()

    with create_db_app().app_context():
        if args.no_op:
            count = db.session.execute(text('SELECT COUNT(*) FROM jita_price_forecasts')).scalar()
            logger.info('Dry-run — jita_price_forecasts currently has %d rows.', count)
            sys.exit(0)
        update_price_forecasts()


if __name__ == '__main__':
    main()
