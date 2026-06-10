"""add user_blueprint_extended view

Revision ID: 58675a25791e
Revises: 883b8b583df6
Create Date: 2026-06-10 18:55:23.164830

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '58675a25791e'
down_revision: Union[str, None] = '883b8b583df6'
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
    b.manufacturing_cost
FROM user_blueprints ub
JOIN users u              ON u.id  = ub.user_id
JOIN blueprints b         ON b.id  = ub.blueprint_id
JOIN eve_items ei         ON ei.id = b.produced_type_id
LEFT JOIN market_groups mg ON mg.id = ei.market_group_id
"""


def upgrade() -> None:
    op.execute(sa.text(_VIEW_SQL))


def downgrade() -> None:
    op.execute(sa.text("DROP VIEW IF EXISTS user_blueprint_extended"))
