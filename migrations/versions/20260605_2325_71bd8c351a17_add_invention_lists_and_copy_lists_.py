"""add invention_lists and copy_lists tables

Revision ID: 71bd8c351a17
Revises: f8440d4211d2
Create Date: 2026-06-05 23:25:45.908004

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '71bd8c351a17'
down_revision: Union[str, None] = 'f8440d4211d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'invention_lists',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('universe_system_id', sa.Integer(), sa.ForeignKey('universe_systems.id'), nullable=False),
        sa.Column('eve_item_id', sa.BigInteger(), sa.ForeignKey('eve_items.id'), nullable=False),
        sa.Column('runs_count', sa.Integer()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_table(
        'copy_lists',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('universe_system_id', sa.Integer(), sa.ForeignKey('universe_systems.id'), nullable=False),
        sa.Column('eve_item_id', sa.BigInteger(), sa.ForeignKey('eve_items.id'), nullable=False),
        sa.Column('runs_count', sa.Integer()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )


def downgrade() -> None:
    op.drop_table('copy_lists')
    op.drop_table('invention_lists')
