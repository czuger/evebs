"""add invented_from_item_slug to user_blueprint_extended view

Revision ID: 01f93a40df71
Revises: fa110ae58235
Create Date: 2026-06-10 23:07:45.049486

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '01f93a40df71'
down_revision: Union[str, None] = 'fa110ae58235'
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
    t1.name                 AS invented_from_name,
    t1_ei.slug              AS invented_from_item_slug
FROM user_blueprints ub
JOIN users u               ON u.id  = ub.user_id
JOIN blueprints b          ON b.id  = ub.blueprint_id
JOIN eve_items ei          ON ei.id = b.produced_type_id
LEFT JOIN market_groups mg ON mg.id = ei.market_group_id
LEFT JOIN blueprints t1    ON t1.id = b.is_invented_from_id
LEFT JOIN eve_items t1_ei  ON t1_ei.id = b.is_invented_from_id
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
    b.is_invented_from_id,
    t1.name                 AS invented_from_name
FROM user_blueprints ub
JOIN users u               ON u.id  = ub.user_id
JOIN blueprints b          ON b.id  = ub.blueprint_id
JOIN eve_items ei          ON ei.id = b.produced_type_id
LEFT JOIN market_groups mg ON mg.id = ei.market_group_id
LEFT JOIN blueprints t1    ON t1.id = b.is_invented_from_id
"""


def upgrade() -> None:
    op.execute(sa.text("DROP VIEW IF EXISTS user_blueprint_extended"))
    op.execute(sa.text(_VIEW_SQL))


def downgrade() -> None:
    op.execute(sa.text("DROP VIEW IF EXISTS user_blueprint_extended"))
    op.execute(sa.text(_OLD_VIEW_SQL))
