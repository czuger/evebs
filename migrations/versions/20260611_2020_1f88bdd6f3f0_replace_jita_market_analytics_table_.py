"""replace jita_market_analytics table with jita_min_prices materialized view

Revision ID: 1f88bdd6f3f0
Revises: 746cfb953796
Create Date: 2026-06-11 20:20:09.944816

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1f88bdd6f3f0'
down_revision: Union[str, None] = '746cfb953796'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_MV_SQL = """
CREATE MATERIALIZED VIEW jita_min_prices AS
WITH sell AS (
    SELECT
        pto.eve_item_id,
        pto.price,
        SUM(pto.volume_remain) OVER (
            PARTITION BY pto.eve_item_id
            ORDER BY pto.price ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cum_vol,
        SUM(pto.volume_remain) OVER (PARTITION BY pto.eve_item_id) AS total_vol
    FROM public_trade_orders pto
    WHERE pto.is_buy_order = FALSE
      AND pto.universe_system_id = 30000142
)
SELECT eve_item_id AS id, MIN(price) AS min_sell_price, now() AS updated_at
FROM sell
WHERE cum_vol >= total_vol * 0.10
GROUP BY eve_item_id
WITH NO DATA
"""

_USER_SALE_ORDER_DETAILS_SQL = """
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
LEFT JOIN jita_min_prices jma ON jma.id = uso.eve_item_id
"""

_USER_INDUSTRY_COSTS_SQL = """
CREATE VIEW user_industry_costs AS
WITH mat_costs AS (
    SELECT
        b.id               AS blueprint_id,
        b.produced_type_id,
        b.activity_type,
        b.prod_qtt,
        b.name,
        SUM((entry.value->>'quantity')::numeric * jma.min_sell_price) AS batch_mat_cost
    FROM blueprints b
    CROSS JOIN LATERAL jsonb_each(b.manufacturing_tree::jsonb) AS entry(key, value)
    LEFT JOIN jita_min_prices jma ON jma.id = entry.key::int
    WHERE b.activity_type IN ('manufacturing', 'reaction')
      AND b.manufacturing_tree IS NOT NULL
      AND b.prod_qtt > 0
    GROUP BY b.id, b.produced_type_id, b.activity_type, b.prod_qtt, b.name
    HAVING COUNT(*) = COUNT(jma.id)
)
SELECT
    u.id                                                                   AS user_id,
    u.name                                                                 AS user_name,
    mc.blueprint_id,
    mc.produced_type_id,
    mc.activity_type,
    mc.name                                                                AS blueprint_name,
    ei.name                                                                AS item_name,
    ei.slug                                                                AS item_slug,
    COALESCE((mc.batch_mat_cost / mc.prod_qtt)::double precision, 0)      AS mat_cost_per_unit,
    COALESCE(
        CASE mc.activity_type
          WHEN 'manufacturing' THEN
            (mc.batch_mat_cost / mc.prod_qtt) *
            ( COALESCE((u.industry_taxes->'manufacturing'->>'system_cost_index')::numeric, 5)
            + COALESCE((u.industry_taxes->'manufacturing'->>'scc_tax')::numeric,           4)
            + COALESCE((u.industry_taxes->'manufacturing'->>'standard_tax')::numeric,      1)
            ) / 100
          WHEN 'reaction' THEN
            (mc.batch_mat_cost / mc.prod_qtt) *
            ( COALESCE((u.industry_taxes->'reaction'->>'system_cost_index')::numeric, 5)
            + COALESCE((u.industry_taxes->'reaction'->>'scc_tax')::numeric,           4)
            + COALESCE((u.industry_taxes->'reaction'->>'reaction_tax')::numeric,      1)
            ) / 100
        END::double precision,
    0)                                                                     AS ind_tax_per_unit,
    COALESCE(jma_prod.min_sell_price::double precision, 0)                AS jita_sell_price
FROM mat_costs mc
CROSS JOIN users u
JOIN eve_items ei ON ei.id = mc.produced_type_id
JOIN jita_min_prices jma_prod ON jma_prod.id = mc.produced_type_id
"""


def upgrade() -> None:
    conn = op.get_bind()
    # Drop the two views that depend on the jita_market_analytics table.
    conn.execute(sa.text('DROP VIEW IF EXISTS user_sale_order_details'))
    conn.execute(sa.text('DROP VIEW IF EXISTS user_industry_costs'))
    conn.execute(sa.text('DROP TABLE jita_market_analytics'))

    conn.execute(sa.text(_MV_SQL))
    conn.execute(sa.text('CREATE UNIQUE INDEX ix_jita_min_prices_id ON jita_min_prices (id)'))
    conn.execute(sa.text('REFRESH MATERIALIZED VIEW jita_min_prices'))

    # Recreate the dependent views against jita_min_prices.
    conn.execute(sa.text(_USER_INDUSTRY_COSTS_SQL))
    conn.execute(sa.text(_USER_SALE_ORDER_DETAILS_SQL))


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
