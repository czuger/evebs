"""create trade_route_buys table

Revision ID: 2a7fce6a77c3
Revises: e8c421a3730c
Create Date: 2026-06-17 12:51:05.373582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '2a7fce6a77c3'
down_revision: Union[str, None] = 'e8c421a3730c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'trade_route_buys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('eve_item_id', sa.BigInteger(), nullable=False),
        sa.Column('src_hub_id', sa.Integer(), nullable=False),
        sa.Column('dst_hub_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['eve_item_id'], ['eve_items.id']),
        sa.ForeignKeyConstraint(['src_hub_id'], ['universe_systems.id']),
        sa.ForeignKeyConstraint(['dst_hub_id'], ['universe_systems.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'eve_item_id', 'src_hub_id', 'dst_hub_id',
                            name='uq_trade_route_buys_user_item_route'),
    )


def downgrade() -> None:
    op.drop_table('trade_route_buys')
