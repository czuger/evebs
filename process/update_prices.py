"""Update buy_orders_analytics from public trade order data."""
import logging
from datetime import datetime
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
