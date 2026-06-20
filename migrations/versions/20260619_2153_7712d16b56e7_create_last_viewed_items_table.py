"""create last_viewed_items table

Revision ID: 7712d16b56e7
Revises: 79f78d69e69f
Create Date: 2026-06-19 21:53:53.431639

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7712d16b56e7'
down_revision: Union[str, None] = '79f78d69e69f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_last_viewed_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('eve_item_id', sa.BigInteger(), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('viewed_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['eve_item_id'], ['eve_items.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'eve_item_id', name='uq_user_last_viewed_items_user_item'),
    )


def downgrade() -> None:
    op.drop_table('user_last_viewed_items')
