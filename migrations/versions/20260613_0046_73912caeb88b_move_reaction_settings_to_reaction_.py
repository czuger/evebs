"""move reaction settings to reaction_modifications

Revision ID: 73912caeb88b
Revises: 307283ad699f
Create Date: 2026-06-13 00:46:29.505793

Move the per-user reaction tax settings out of industry_taxes['reaction'] into a dedicated
reaction_modifications JSON column (adding material_consumption, default 0), and recreate the
user_industry_costs view so its reaction branch reads the new column.
"""
import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '73912caeb88b'
down_revision: Union[str, None] = '307283ad699f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _view_sql(reaction_source: str) -> str:
    """user_industry_costs view; reaction tax keys read from `reaction_source` (a JSON expr)."""
    return f"""
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
            ( COALESCE(({reaction_source}->>'system_cost_index')::numeric, 5)
            + COALESCE(({reaction_source}->>'scc_tax')::numeric,           4)
            + COALESCE(({reaction_source}->>'reaction_tax')::numeric,      1)
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
    op.add_column('users', sa.Column('reaction_modifications', sa.JSON(), nullable=True))

    # Backfill from industry_taxes['reaction'] and strip the key out of industry_taxes.
    rows = conn.execute(sa.text('SELECT id, industry_taxes FROM users')).all()
    for uid, taxes in rows:
        taxes = taxes if isinstance(taxes, dict) else json.loads(taxes or '{}')
        rxn = taxes.pop('reaction', None) or {}
        mods = {
            'system_cost_index': rxn.get('system_cost_index', 5.0),
            'scc_tax':           rxn.get('scc_tax', 4.0),
            'reaction_tax':      rxn.get('reaction_tax', 1.0),
            'material_consumption': 0,
        }
        conn.execute(
            sa.text('UPDATE users SET reaction_modifications = :m, industry_taxes = :t WHERE id = :id'),
            {'m': json.dumps(mods), 't': json.dumps(taxes), 'id': uid})

    op.alter_column('users', 'reaction_modifications', nullable=False)

    op.execute('DROP VIEW IF EXISTS user_industry_costs')
    op.execute(_view_sql("u.reaction_modifications"))


def downgrade() -> None:
    conn = op.get_bind()
    op.execute('DROP VIEW IF EXISTS user_industry_costs')

    # Restore the reaction key into industry_taxes from reaction_modifications.
    rows = conn.execute(sa.text('SELECT id, industry_taxes, reaction_modifications FROM users')).all()
    for uid, taxes, mods in rows:
        taxes = taxes if isinstance(taxes, dict) else json.loads(taxes or '{}')
        mods = mods if isinstance(mods, dict) else json.loads(mods or '{}')
        taxes['reaction'] = {
            'system_cost_index': mods.get('system_cost_index', 5.0),
            'scc_tax':           mods.get('scc_tax', 4.0),
            'reaction_tax':      mods.get('reaction_tax', 1.0),
        }
        conn.execute(sa.text('UPDATE users SET industry_taxes = :t WHERE id = :id'),
                     {'t': json.dumps(taxes), 'id': uid})

    op.drop_column('users', 'reaction_modifications')
    op.execute(_view_sql("u.industry_taxes->'reaction'"))
