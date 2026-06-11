"""rename is_invented_by to is_invented_from on blueprints

Revision ID: 89c1f844a107
Revises: 0e93fe8b752b
Create Date: 2026-06-10 19:58:07.902745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '89c1f844a107'
down_revision: Union[str, None] = '0e93fe8b752b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('fk_blueprints_is_invented_by', 'blueprints', type_='foreignkey')
    op.alter_column('blueprints', 'is_invented_by', new_column_name='is_invented_from')
    op.create_foreign_key(
        'fk_blueprints_is_invented_from',
        'blueprints', 'blueprints',
        ['is_invented_from'], ['id'],
    )


def downgrade() -> None:
    op.drop_constraint('fk_blueprints_is_invented_from', 'blueprints', type_='foreignkey')
    op.alter_column('blueprints', 'is_invented_from', new_column_name='is_invented_by')
    op.create_foreign_key(
        'fk_blueprints_is_invented_by',
        'blueprints', 'blueprints',
        ['is_invented_by'], ['id'],
    )
