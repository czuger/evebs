"""add is_invented_by to blueprints

Revision ID: 0e93fe8b752b
Revises: 58675a25791e
Create Date: 2026-06-10 19:24:40.471714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0e93fe8b752b'
down_revision: Union[str, None] = '58675a25791e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('blueprints', sa.Column('is_invented_by', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_blueprints_is_invented_by',
        'blueprints', 'blueprints',
        ['is_invented_by'], ['id'],
    )


def downgrade() -> None:
    op.drop_constraint('fk_blueprints_is_invented_by', 'blueprints', type_='foreignkey')
    op.drop_column('blueprints', 'is_invented_by')
