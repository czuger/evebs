"""Update buy_orders_analytics and weekly_price_details from trade order / sales data."""
import logging
from datetime import datetime, timedelta
from sqlalchemy import text
from evebs.extensions import db

logger = logging.getLogger(__name__)


def update_buy_orders_analytics():
    logger.debug('Updating buy orders analytics...')
    now = datetime.utcnow()

    db.session.execute(text("""
        INSERT INTO buy_orders_analytics (universe_system_id, eve_item_id, approx_max_price, created_at, updated_at)
        SELECT universe_system_id, eve_item_id, MAX(price) * 0.9, :now, :now
        FROM public_trade_orders
        WHERE is_buy_order = TRUE
        GROUP BY universe_system_id, eve_item_id
        ON CONFLICT (universe_system_id, eve_item_id)
        DO UPDATE SET approx_max_price = excluded.approx_max_price, updated_at = :now
    """), {'now': now})

    db.session.execute(text("""
        UPDATE buy_orders_analytics SET over_approx_max_price_volume = (
            SELECT SUM(volume_remain)
            FROM public_trade_orders bo
            WHERE bo.price >= buy_orders_analytics.approx_max_price
            AND bo.universe_system_id = buy_orders_analytics.universe_system_id
            AND bo.eve_item_id = buy_orders_analytics.eve_item_id
            AND bo.is_buy_order = TRUE
        )
    """))

    db.session.execute(text("""
        UPDATE buy_orders_analytics SET
            single_unit_cost = (
                SELECT b.manufacturing_cost / NULLIF(b.prod_qtt, 0)
                FROM blueprints b
                JOIN eve_items ei ON ei.blueprint_id = b.id
                WHERE ei.id = buy_orders_analytics.eve_item_id
                  AND b.manufacturing_cost IS NOT NULL
                  AND b.prod_qtt > 0
            ),
            single_unit_margin = approx_max_price - (
                SELECT b.manufacturing_cost / NULLIF(b.prod_qtt, 0)
                FROM blueprints b
                JOIN eve_items ei ON ei.blueprint_id = b.id
                WHERE ei.id = buy_orders_analytics.eve_item_id
                  AND b.manufacturing_cost IS NOT NULL
                  AND b.prod_qtt > 0
            )
    """))

    db.session.execute(text("""
        UPDATE buy_orders_analytics SET
            estimated_volume_margin = single_unit_margin * over_approx_max_price_volume,
            final_margin = LEAST(
                single_unit_margin * over_approx_max_price_volume,
                single_unit_margin * (
                    SELECT nb_runs * prod_qtt FROM blueprints
                    JOIN eve_items ON eve_items.blueprint_id = blueprints.id
                    WHERE eve_items.id = buy_orders_analytics.eve_item_id
                )
            )
        WHERE single_unit_margin IS NOT NULL
    """))

    db.session.commit()
    logger.debug('Buy orders analytics updated.')


def update_weekly_price_details():
    logger.debug('Updating weekly price details...')
    now = datetime.utcnow()
    yesterday = (now.date() - timedelta(days=1)).isoformat()
    week_ago = (now.date() - timedelta(days=7)).isoformat()

    db.session.execute(text("""
        INSERT INTO weekly_price_details (eve_item_id, universe_system_id, day, volume, weighted_avg_price, created_at, updated_at)
        SELECT sf.eve_item_id, sf.universe_system_id, sf.day,
               SUM(sf.volume),
               SUM(sf.volume * sf.price) / SUM(sf.volume),
               :now, :now
        FROM sales_finals sf
        WHERE sf.day > :yesterday AND sf.volume > 0
        GROUP BY sf.eve_item_id, sf.universe_system_id, sf.day
        ON CONFLICT (eve_item_id, universe_system_id, day)
        DO UPDATE SET
            volume = excluded.volume,
            weighted_avg_price = excluded.weighted_avg_price,
            updated_at = :now
    """), {'now': now, 'yesterday': yesterday})

    db.session.execute(text("""
        DELETE FROM weekly_price_details WHERE day < :week_ago
    """), {'week_ago': week_ago})

    db.session.commit()
    logger.debug('Weekly price details updated.')
