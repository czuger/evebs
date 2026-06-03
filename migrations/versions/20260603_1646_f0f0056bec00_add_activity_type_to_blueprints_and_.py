"""add activity_type to blueprints and jita_reaction_margins view

Revision ID: f0f0056bec00
Revises: a0e132bfde89
Create Date: 2026-06-03 16:46:36.146379

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f0f0056bec00'
down_revision: Union[str, None] = 'a0e132bfde89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Add activity_type column; existing rows are all manufacturing blueprints
    conn.execute(sa.text(
        "ALTER TABLE blueprints ADD COLUMN activity_type VARCHAR(20) NOT NULL DEFAULT 'manufacturing'"
    ))

    # Recreate jita_manufacturing_margins filtered to manufacturing blueprints only
    conn.execute(sa.text('DROP MATERIALIZED VIEW IF EXISTS jita_manufacturing_margins'))
    conn.execute(sa.text("""
        CREATE MATERIALIZED VIEW jita_manufacturing_margins AS
        WITH mat_costs AS (
            SELECT
                b.produced_type_id,
                b.prod_qtt,
                SUM(bm.required_qtt::bigint * jp.min_sell_price) AS manufacturing_cost
            FROM blueprints b
            JOIN blueprint_materials bm ON bm.blueprint_id = b.id
            JOIN eve_items ei_mat ON ei_mat.id = bm.eve_item_id
            JOIN jita_prices jp ON jp.id = ei_mat.id
            WHERE b.activity_type = 'manufacturing'
            GROUP BY b.produced_type_id, b.prod_qtt
        )
        SELECT
            mc.produced_type_id                                       AS id,
            ei.id                                                         AS eve_item_id,
            mc.manufacturing_cost,
            mc.manufacturing_cost * 0.10                                  AS manufacturing_tax,
            mc.prod_qtt::bigint * jp_prod.min_sell_price                  AS estimated_selling_price,
            mc.prod_qtt::bigint * jp_prod.min_sell_price * 0.05           AS selling_tax,
            (mc.prod_qtt::bigint * jp_prod.min_sell_price)
                - (mc.prod_qtt::bigint * jp_prod.min_sell_price * 0.05)
                - mc.manufacturing_cost
                - (mc.manufacturing_cost * 0.10)                          AS benefit
        FROM mat_costs mc
        JOIN eve_items ei        ON ei.id        = mc.produced_type_id
        JOIN jita_prices jp_prod ON jp_prod.id   = mc.produced_type_id
        WITH NO DATA
    """))
    conn.execute(sa.text('CREATE UNIQUE INDEX ON jita_manufacturing_margins (id)'))

    # Create jita_reaction_margins
    conn.execute(sa.text("""
        CREATE MATERIALIZED VIEW jita_reaction_margins AS
        WITH mat_costs AS (
            SELECT
                b.produced_type_id,
                b.prod_qtt,
                SUM(bm.required_qtt::bigint * jp.min_sell_price) AS reaction_cost
            FROM blueprints b
            JOIN blueprint_materials bm ON bm.blueprint_id = b.id
            JOIN eve_items ei_mat ON ei_mat.id = bm.eve_item_id
            JOIN jita_prices jp ON jp.id = ei_mat.id
            WHERE b.activity_type = 'reaction'
            GROUP BY b.produced_type_id, b.prod_qtt
        )
        SELECT
            mc.produced_type_id                                       AS id,
            ei.id                                                         AS eve_item_id,
            mc.reaction_cost,
            mc.prod_qtt::bigint * jp_prod.min_sell_price                  AS estimated_selling_price,
            mc.prod_qtt::bigint * jp_prod.min_sell_price * 0.05           AS selling_tax,
            (mc.prod_qtt::bigint * jp_prod.min_sell_price)
                - (mc.prod_qtt::bigint * jp_prod.min_sell_price * 0.05)
                - mc.reaction_cost                                         AS benefit
        FROM mat_costs mc
        JOIN eve_items ei        ON ei.id        = mc.produced_type_id
        JOIN jita_prices jp_prod ON jp_prod.id   = mc.produced_type_id
        WITH NO DATA
    """))
    conn.execute(sa.text('CREATE UNIQUE INDEX ON jita_reaction_margins (id)'))


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
