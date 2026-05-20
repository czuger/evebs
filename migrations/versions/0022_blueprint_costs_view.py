"""Add blueprint_costs SQL view (cost/margin per blueprint × system).

Revision ID: 0022_blueprint_costs_view
Revises: 0021_market_percentiles
Create Date: 2026-05-20

"""
from alembic import op

revision = '0022_blueprint_costs_view'
down_revision = '0021_market_percentiles'
branch_labels = None
depends_on = None

_VIEW_SQL = """
CREATE VIEW blueprint_costs AS
WITH material_costs AS (
    SELECT
        bm.blueprint_id,
        msp.system_id,
        SUM(bm.required_qtt * b.nb_runs * msp.p10_price) AS raw_material_cost,
        COUNT(DISTINCT bm.id)                              AS priced_line_count
    FROM blueprint_materials bm
    JOIN blueprints b             ON b.id        = bm.blueprint_id
    JOIN market_seller_prices msp ON msp.type_id = bm.universe_type_id
    GROUP BY bm.blueprint_id, b.nb_runs, msp.system_id
),
blueprint_totals AS (
    SELECT blueprint_id, COUNT(*) AS total_material_count
    FROM blueprint_materials
    GROUP BY blueprint_id
)
SELECT
    b.id                                                             AS blueprint_id,
    mc.system_id,
    b.name                                                           AS blueprint_name,
    b.produced_type_id,
    us.name                                                          AS system_name,
    b.nb_runs,
    b.prod_qtt,
    b.nb_runs * b.prod_qtt                                          AS batch_elements_count,
    mc.raw_material_cost,
    mc.raw_material_cost / NULLIF(b.nb_runs * b.prod_qtt, 0)       AS cost_per_unit,
    mbp.p90_price                                                    AS sell_price_per_unit,
    mbp.p90_price * (b.nb_runs * b.prod_qtt)                       AS batch_sell_value,
    mbp.volume                                                       AS produced_sell_volume,
    mbp.p90_price
        - mc.raw_material_cost / NULLIF(b.nb_runs * b.prod_qtt, 0) AS margin_per_unit,
    CASE
        WHEN mc.raw_material_cost > 0 AND mbp.p90_price IS NOT NULL
        THEN (
            (mbp.p90_price - mc.raw_material_cost / (b.nb_runs * b.prod_qtt))
            / (mc.raw_material_cost / (b.nb_runs * b.prod_qtt))
        ) * 100
        ELSE NULL
    END                                                              AS roi_percent,
    mc.priced_line_count < bt.total_material_count                   AS has_missing_prices,
    bt.total_material_count                                          AS material_line_count
FROM blueprints b
JOIN material_costs   mc  ON mc.blueprint_id = b.id
JOIN blueprint_totals bt  ON bt.blueprint_id = b.id
JOIN universe_systems us  ON us.id           = mc.system_id
LEFT JOIN market_buyer_prices mbp
       ON mbp.type_id   = b.produced_type_id
      AND mbp.system_id = mc.system_id
"""


def upgrade():
    op.execute(_VIEW_SQL)


def downgrade():
    op.execute("DROP VIEW IF EXISTS blueprint_costs")
