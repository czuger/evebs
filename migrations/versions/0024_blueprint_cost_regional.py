"""Add blueprint_cost_regional view: same as blueprint_costs but aggregated at region level.

Revision ID: 0024_blueprint_cost_regional
Revises: 0023_blueprint_costs_v2
Create Date: 2026-05-20

"""
from alembic import op

revision = '0024_blueprint_cost_regional'
down_revision = '0023_blueprint_costs_v2'
branch_labels = None
depends_on = None

_VIEW_SQL = """
CREATE VIEW blueprint_cost_regional AS
WITH regional_seller_prices AS (
    SELECT
        ms.type_id,
        uc.universe_region_id          AS region_id,
        MIN(ms.p10_price)              AS p10_price
    FROM market_seller_prices ms
    JOIN universe_systems        us ON us.id = ms.system_id
    JOIN universe_constellations uc ON uc.id = us.universe_constellation_id
    WHERE uc.universe_region_id IS NOT NULL
    GROUP BY ms.type_id, uc.universe_region_id
),
regional_buyer_prices AS (
    SELECT
        mb.type_id,
        uc.universe_region_id          AS region_id,
        MAX(mb.p90_price)              AS p90_price,
        SUM(mb.volume)                 AS volume
    FROM market_buyer_prices mb
    JOIN universe_systems        us ON us.id = mb.system_id
    JOIN universe_constellations uc ON uc.id = us.universe_constellation_id
    WHERE uc.universe_region_id IS NOT NULL
    GROUP BY mb.type_id, uc.universe_region_id
),
material_costs_sell AS (
    SELECT
        bm.blueprint_id,
        rsp.region_id,
        SUM(bm.required_qtt * b.nb_runs * rsp.p10_price) AS material_cost_sell,
        COUNT(DISTINCT bm.id)                              AS priced_line_count
    FROM blueprint_materials bm
    JOIN blueprints              b  ON b.id        = bm.blueprint_id
    JOIN regional_seller_prices rsp ON rsp.type_id = bm.universe_type_id
    GROUP BY bm.blueprint_id, b.nb_runs, rsp.region_id
),
material_values_buy AS (
    SELECT
        bm.blueprint_id,
        rbp.region_id,
        SUM(bm.required_qtt * b.nb_runs * rbp.p90_price) AS material_value_buy
    FROM blueprint_materials bm
    JOIN blueprints              b  ON b.id        = bm.blueprint_id
    JOIN regional_buyer_prices  rbp ON rbp.type_id = bm.universe_type_id
    GROUP BY bm.blueprint_id, b.nb_runs, rbp.region_id
),
blueprint_totals AS (
    SELECT blueprint_id, COUNT(*) AS total_material_count
    FROM blueprint_materials
    GROUP BY blueprint_id
)
SELECT
    b.id                                                                   AS blueprint_id,
    mc.region_id,
    b.name                                                                 AS blueprint_name,
    b.produced_type_id,
    ur.name                                                                AS region_name,
    b.nb_runs,
    b.prod_qtt,
    b.nb_runs * b.prod_qtt                                                AS batch_elements_count,
    mc.material_cost_sell,
    mc.material_cost_sell / NULLIF(b.nb_runs * b.prod_qtt, 0)            AS cost_per_unit_sell,
    mv.material_value_buy,
    mv.material_value_buy / NULLIF(b.nb_runs * b.prod_qtt, 0)            AS value_per_unit_buy,
    rbp.p90_price                                                          AS output_price_buy,
    rbp.p90_price * (b.nb_runs * b.prod_qtt)                             AS batch_revenue_buy,
    rbp.volume                                                             AS output_volume_buy,
    rbp.p90_price
        - mc.material_cost_sell / NULLIF(b.nb_runs * b.prod_qtt, 0)      AS margin_per_unit,
    rbp.p90_price
        - mv.material_value_buy / NULLIF(b.nb_runs * b.prod_qtt, 0)      AS craft_vs_sell_margin,
    CASE
        WHEN mc.material_cost_sell > 0 AND rbp.p90_price IS NOT NULL
        THEN (
            (rbp.p90_price - mc.material_cost_sell / (b.nb_runs * b.prod_qtt))
            / (mc.material_cost_sell / (b.nb_runs * b.prod_qtt))
        ) * 100
        ELSE NULL
    END                                                                    AS roi_percent,
    mc.priced_line_count < bt.total_material_count                         AS has_missing_prices,
    bt.total_material_count                                                AS material_line_count
FROM blueprints b
JOIN material_costs_sell mc  ON mc.blueprint_id = b.id
JOIN blueprint_totals    bt  ON bt.blueprint_id = b.id
JOIN universe_regions    ur  ON ur.id           = mc.region_id
LEFT JOIN material_values_buy mv
       ON mv.blueprint_id = b.id
      AND mv.region_id    = mc.region_id
LEFT JOIN regional_buyer_prices rbp
       ON rbp.type_id   = b.produced_type_id
      AND rbp.region_id = mc.region_id
"""


def upgrade():
    op.execute(_VIEW_SQL)


def downgrade():
    op.execute("DROP VIEW IF EXISTS blueprint_cost_regional")
