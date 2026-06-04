"""add manufacturing_cost to blueprints, drop blueprint_materials, simplify views

Revision ID: 36d771e4f49c
Revises: f0f0056bec00
Create Date: 2026-06-03 22:43:23.865607

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '36d771e4f49c'
down_revision: Union[str, None] = 'f0f0056bec00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    conn.execute(sa.text('ALTER TABLE blueprints ADD COLUMN manufacturing_cost FLOAT'))

    # Drop materialized views and plain view that depend on blueprint_materials
    conn.execute(sa.text('DROP MATERIALIZED VIEW IF EXISTS jita_manufacturing_margins'))
    conn.execute(sa.text('DROP MATERIALIZED VIEW IF EXISTS jita_reaction_margins'))
    conn.execute(sa.text('DROP VIEW IF EXISTS components_to_buys'))

    # Recreate jita_manufacturing_margins using the pre-computed column
    conn.execute(sa.text("""
        CREATE MATERIALIZED VIEW jita_manufacturing_margins AS
        SELECT
            b.produced_type_id                                        AS id,
            ei.id                                                     AS eve_item_id,
            b.manufacturing_cost,
            b.manufacturing_cost * 0.10                               AS manufacturing_tax,
            b.prod_qtt::bigint * jp.min_sell_price                    AS estimated_selling_price,
            b.prod_qtt::bigint * jp.min_sell_price * 0.05             AS selling_tax,
            (b.prod_qtt::bigint * jp.min_sell_price)
                - (b.prod_qtt::bigint * jp.min_sell_price * 0.05)
                - b.manufacturing_cost
                - (b.manufacturing_cost * 0.10)                       AS benefit
        FROM blueprints b
        JOIN eve_items ei        ON ei.id = b.produced_type_id
        JOIN jita_prices jp      ON jp.id = b.produced_type_id
        WHERE b.activity_type = 'manufacturing'
          AND b.manufacturing_cost IS NOT NULL
        WITH NO DATA
    """))
    conn.execute(sa.text('CREATE UNIQUE INDEX ON jita_manufacturing_margins (id)'))

    # Recreate jita_reaction_margins using the pre-computed column (no manufacturing tax)
    conn.execute(sa.text("""
        CREATE MATERIALIZED VIEW jita_reaction_margins AS
        SELECT
            b.produced_type_id                                        AS id,
            ei.id                                                     AS eve_item_id,
            b.manufacturing_cost                                      AS reaction_cost,
            b.prod_qtt::bigint * jp.min_sell_price                    AS estimated_selling_price,
            b.prod_qtt::bigint * jp.min_sell_price * 0.05             AS selling_tax,
            (b.prod_qtt::bigint * jp.min_sell_price)
                - (b.prod_qtt::bigint * jp.min_sell_price * 0.05)
                - b.manufacturing_cost                                 AS benefit
        FROM blueprints b
        JOIN eve_items ei        ON ei.id = b.produced_type_id
        JOIN jita_prices jp      ON jp.id = b.produced_type_id
        WHERE b.activity_type = 'reaction'
          AND b.manufacturing_cost IS NOT NULL
        WITH NO DATA
    """))
    conn.execute(sa.text('CREATE UNIQUE INDEX ON jita_reaction_margins (id)'))

    conn.execute(sa.text('DROP TABLE IF EXISTS blueprint_materials'))


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
