"""Remove 100-run factor from jita_manufacturing_margins: compute per-run cost

Revision ID: e6f7a8b9c0d1
Revises: d5e6f7a8b9c0
Create Date: 2026-05-29

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'e6f7a8b9c0d1'
down_revision: Union[str, None] = 'd5e6f7a8b9c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CREATE_MV = """
CREATE MATERIALIZED VIEW jita_manufacturing_margins AS
WITH mat_costs AS (
    SELECT
        b.produced_cpp_type_id,
        b.prod_qtt,
        SUM(bm.required_qtt::bigint * jp.min_sell_price) AS manufacturing_cost
    FROM blueprints b
    JOIN blueprint_materials bm ON bm.blueprint_id = b.id
    JOIN eve_items ei_mat ON ei_mat.id = bm.eve_item_id
    JOIN jita_prices jp ON jp.cpp_eve_item_id = ei_mat.cpp_eve_item_id
    GROUP BY b.produced_cpp_type_id, b.prod_qtt
)
SELECT
    mc.produced_cpp_type_id                                      AS cpp_eve_item_id,
    ei.id                                                        AS eve_item_id,
    mc.manufacturing_cost,
    mc.manufacturing_cost * 0.10                                 AS manufacturing_tax,
    mc.prod_qtt::bigint * jp_prod.min_sell_price                  AS estimated_selling_price,
    mc.prod_qtt::bigint * jp_prod.min_sell_price * 0.05           AS selling_tax,
    (mc.prod_qtt::bigint * jp_prod.min_sell_price)
        - (mc.prod_qtt::bigint * jp_prod.min_sell_price * 0.05)
        - mc.manufacturing_cost
        - (mc.manufacturing_cost * 0.10)                         AS benefit
FROM mat_costs mc
JOIN eve_items ei        ON ei.cpp_eve_item_id   = mc.produced_cpp_type_id
JOIN jita_prices jp_prod ON jp_prod.cpp_eve_item_id = mc.produced_cpp_type_id
WITH NO DATA
"""


def upgrade() -> None:
    op.execute('DROP MATERIALIZED VIEW IF EXISTS jita_manufacturing_margins')
    op.execute(CREATE_MV)
    op.execute('CREATE UNIQUE INDEX ON jita_manufacturing_margins (cpp_eve_item_id)')


def downgrade() -> None:
    op.execute('DROP MATERIALIZED VIEW IF EXISTS jita_manufacturing_margins')
