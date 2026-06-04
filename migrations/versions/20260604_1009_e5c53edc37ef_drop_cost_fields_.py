"""drop cost fields, EveMarketHistoriesGroup, PricesAdvice, PricesMin; update views

Revision ID: e5c53edc37ef
Revises: 662440072523
Create Date: 2026-06-04 10:09:41.825752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e5c53edc37ef'
down_revision: Union[str, None] = '662440072523'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Drop views that depend on tables being removed
    conn.execute(sa.text('DROP VIEW IF EXISTS price_advices_min_prices'))
    conn.execute(sa.text('DROP VIEW IF EXISTS price_advice_margin_comps'))
    conn.execute(sa.text('DROP VIEW IF EXISTS user_sale_order_details'))

    # Drop tables
    conn.execute(sa.text('DROP TABLE IF EXISTS prices_mins'))
    conn.execute(sa.text('DROP TABLE IF EXISTS prices_advices'))
    conn.execute(sa.text('DROP TABLE IF EXISTS eve_market_histories_groups'))

    # Drop columns from eve_items
    conn.execute(sa.text("""
        ALTER TABLE eve_items
            DROP COLUMN IF EXISTS cost,
            DROP COLUMN IF EXISTS weekly_avg_price,
            DROP COLUMN IF EXISTS cpp_market_average_price,
            DROP COLUMN IF EXISTS cpp_market_adjusted_price
    """))

    # Recreate user_sale_order_details using jita_market_analytics instead of prices_mins
    conn.execute(sa.text("""
        CREATE VIEW user_sale_order_details AS
        SELECT
            uso.id,
            uso.user_id,
            (us.name || ' (' || ur.name || ')') AS trade_hub_name,
            ei.name AS eve_item_name,
            uso.price AS my_price,
            jma.min_sell_price AS min_price,
            b.manufacturing_cost / NULLIF(b.prod_qtt, 0) AS cost,
            b.prod_qtt,
            (jma.min_sell_price / NULLIF(b.manufacturing_cost / NULLIF(b.prod_qtt, 0), 0) - 1.0)
                AS min_price_margin_pcent,
            (jma.min_sell_price - uso.price) AS price_delta,
            uso.eve_item_id,
            uso.universe_system_id AS trade_hub_id,
            us.id AS eve_system_id
        FROM user_sale_orders uso
        JOIN eve_items ei ON ei.id = uso.eve_item_id
        LEFT JOIN blueprints b ON ei.blueprint_id = b.id
        JOIN universe_systems us ON uso.universe_system_id = us.id
        JOIN universe_constellations uc ON us.universe_constellation_id = uc.id
        JOIN universe_regions ur ON uc.universe_region_id = ur.id
        LEFT JOIN jita_market_analytics jma ON jma.id = uso.eve_item_id
    """))


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
