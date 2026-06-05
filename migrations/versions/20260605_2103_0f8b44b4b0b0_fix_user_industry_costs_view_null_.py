"""Fix user_industry_costs view null handling

Revision ID: 0f8b44b4b0b0
Revises: fafa255d0c13
Create Date: 2026-06-05 21:03:50.553254

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0f8b44b4b0b0'
down_revision: Union[str, None] = 'fafa255d0c13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_VIEW_SQL = """
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
    LEFT JOIN jita_market_analytics jma ON jma.id = entry.key::int
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
JOIN jita_market_analytics jma_prod ON jma_prod.id = mc.produced_type_id
"""


def upgrade() -> None:
    op.execute(sa.text("DROP VIEW IF EXISTS user_industry_costs"))
    op.execute(sa.text(_VIEW_SQL))


def downgrade() -> None:
    op.execute(sa.text("DROP VIEW IF EXISTS user_industry_costs"))
