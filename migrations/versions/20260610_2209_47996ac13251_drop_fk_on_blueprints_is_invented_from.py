"""drop fk on blueprints is_invented_from

Revision ID: 47996ac13251
Revises: 89c1f844a107
Create Date: 2026-06-10 22:09:15.992534

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '47996ac13251'
down_revision: Union[str, None] = '89c1f844a107'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('fk_blueprints_is_invented_from', 'blueprints', type_='foreignkey')


def downgrade() -> None:
    op.create_foreign_key(
        'fk_blueprints_is_invented_from',
        'blueprints', 'blueprints',
        ['is_invented_from'], ['id'],
    )
