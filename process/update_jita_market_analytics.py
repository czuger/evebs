#!/usr/bin/env python3
"""Refresh jita_market_analytics with live Jita min_sell_price and 3-day price forecast.

min_sell_price:  P10 ask price at Jita from public_trade_orders (same algorithm as
                 the jita_prices materialized view).

price_forecast_3d: volume-weighted linear regression over the last 30 days of
                 daily VWAPs from sales_finals at Jita, evaluated at CURRENT_DATE + 3.
"""
import logging
logger = logging.getLogger(__name__)


def update_jita_market_analytics():
    from sqlalchemy import text
    from evebs.extensions import db

    db.session.execute(text("""
        INSERT INTO jita_market_analytics (id, min_sell_price, updated_at)
        WITH
        jita AS (
            SELECT id FROM universe_systems WHERE id = 30000142
        ),
        sell AS (
            SELECT
                pto.eve_item_id,
                pto.price,
                SUM(pto.volume_remain) OVER (
                    PARTITION BY pto.eve_item_id
                    ORDER BY pto.price ASC
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS cum_vol,
                SUM(pto.volume_remain) OVER (
                    PARTITION BY pto.eve_item_id
                ) AS total_vol
            FROM public_trade_orders pto
            WHERE pto.is_buy_order = FALSE
              AND pto.universe_system_id = (SELECT id FROM jita)
        ),
        sell_p10 AS (
            SELECT eve_item_id, MIN(price) AS min_sell_price
            FROM sell
            WHERE cum_vol >= total_vol * 0.10
            GROUP BY eve_item_id
        )
        SELECT eve_item_id, min_sell_price, NOW()
        FROM sell_p10
        ON CONFLICT (id) DO UPDATE SET
            min_sell_price = EXCLUDED.min_sell_price,
            updated_at     = NOW()
    """))

    db.session.execute(text("""
        INSERT INTO jita_market_analytics (id, price_forecast_3d, updated_at)
        WITH
        jita AS (
            SELECT id FROM universe_systems WHERE id = 30000142
        ),
        daily AS (
            SELECT
                eve_item_id,
                EXTRACT(EPOCH FROM day) / 86400.0       AS x,
                SUM(volume * price) / SUM(volume)        AS y,
                SUM(volume)::FLOAT                       AS w
            FROM sales_finals
            WHERE universe_system_id = (SELECT id FROM jita)
              AND day >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY eve_item_id, day
        ),
        agg AS (
            SELECT
                eve_item_id,
                SUM(w)       AS sw,
                SUM(w * x)   AS swx,
                SUM(w * y)   AS swy,
                SUM(w * x*x) AS swxx,
                SUM(w * x*y) AS swxy
            FROM daily
            GROUP BY eve_item_id
            HAVING SUM(w) > 0
        ),
        forecast AS (
            SELECT
                eve_item_id,
                CASE WHEN (sw * swxx - swx * swx) = 0 THEN NULL
                     ELSE swy / sw
                          + ((sw * swxy - swx * swy) / (sw * swxx - swx * swx))
                          * (EXTRACT(EPOCH FROM CURRENT_DATE) / 86400.0 + 3 - swx / sw)
                END AS price_forecast_3d
            FROM agg
        )
        SELECT eve_item_id, price_forecast_3d, NOW()
        FROM forecast
        ON CONFLICT (id) DO UPDATE SET
            price_forecast_3d = EXCLUDED.price_forecast_3d,
            updated_at        = NOW()
    """))

    db.session.commit()

    count = db.session.execute(text('SELECT COUNT(*) FROM jita_market_analytics')).scalar()
    n_forecast = db.session.execute(
        text('SELECT COUNT(*) FROM jita_market_analytics WHERE price_forecast_3d IS NOT NULL')
    ).scalar()
    logger.info(
        'jita_market_analytics updated: %d rows total, %d with price_forecast_3d.',
        count, n_forecast,
    )
    return {'rows': count, 'with_forecast': n_forecast}


if __name__ == '__main__':
    import argparse
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import setup_logging
    setup_logging()

    parser = argparse.ArgumentParser(description='Refresh jita_market_analytics.')
    parser.add_argument('-n', '--no-op', action='store_true',
                        help='Dry-run: print current row count, do not update.')
    args = parser.parse_args()

    from app import app
    with app.app_context():
        if args.no_op:
            from sqlalchemy import text
            from evebs.extensions import db
            count = db.session.execute(text('SELECT COUNT(*) FROM jita_market_analytics')).scalar()
            logger.info('Dry-run — jita_market_analytics currently has %d rows.', count)
            sys.exit(0)
        update_jita_market_analytics()
