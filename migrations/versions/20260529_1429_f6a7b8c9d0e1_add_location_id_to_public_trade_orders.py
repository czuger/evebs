"""Add location_id to public_trade_orders

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-05-29

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('public_trade_orders', sa.Column('location_id', sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column('public_trade_orders', 'location_id')
