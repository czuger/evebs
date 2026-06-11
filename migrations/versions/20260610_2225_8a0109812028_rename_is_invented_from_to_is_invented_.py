"""rename is_invented_from to is_invented_from_id and update view

Revision ID: 8a0109812028
Revises: 4f3657de9f31
Create Date: 2026-06-10 22:25:33.497090

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8a0109812028'
down_revision: Union[str, None] = '4f3657de9f31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_VIEW_SQL = """
CREATE VIEW user_blueprint_extended AS
SELECT
    ub.id,
    ub.user_id,
    u.name                  AS user_name,
    ub.blueprint_id,
    b.name                  AS blueprint_name,
    b.activity_type,
    b.produced_type_id,
    ei.name                 AS item_name,
    ei.slug                 AS item_slug,
    ei.market_group_id,
    mg.name                 AS market_group_name,
    b.nb_runs,
    b.prod_qtt,
    b.manufacturing_cost,
    b.is_invented_from_id,
    t1.name                 AS invented_from_name
FROM user_blueprints ub
JOIN users u               ON u.id              = ub.user_id
JOIN blueprints b          ON b.id              = ub.blueprint_id
JOIN eve_items ei          ON ei.id             = b.produced_type_id
LEFT JOIN market_groups mg ON mg.id             = ei.market_group_id
LEFT JOIN blueprints t1    ON t1.produced_type_id = b.is_invented_from_id
"""

_OLD_VIEW_SQL = """
CREATE VIEW user_blueprint_extended AS
SELECT
    ub.id,
    ub.user_id,
    u.name                  AS user_name,
    ub.blueprint_id,
    b.name                  AS blueprint_name,
    b.activity_type,
    b.produced_type_id,
    ei.name                 AS item_name,
    ei.slug                 AS item_slug,
    ei.market_group_id,
    mg.name                 AS market_group_name,
    b.nb_runs,
    b.prod_qtt,
    b.manufacturing_cost,
    b.is_invented_from,
    t1.name                 AS invented_from_name
FROM user_blueprints ub
JOIN users u               ON u.id  = ub.user_id
JOIN blueprints b          ON b.id  = ub.blueprint_id
JOIN eve_items ei          ON ei.id = b.produced_type_id
LEFT JOIN market_groups mg ON mg.id = ei.market_group_id
LEFT JOIN blueprints t1    ON t1.id = b.is_invented_from
"""


def upgrade() -> None:
    op.execute(sa.text("DROP VIEW IF EXISTS user_blueprint_extended"))
    op.alter_column('blueprints', 'is_invented_from', new_column_name='is_invented_from_id')
    op.execute(sa.text(_VIEW_SQL))


def downgrade() -> None:
    op.execute(sa.text("DROP VIEW IF EXISTS user_blueprint_extended"))
    op.alter_column('blueprints', 'is_invented_from_id', new_column_name='is_invented_from')
    op.execute(sa.text(_OLD_VIEW_SQL))
