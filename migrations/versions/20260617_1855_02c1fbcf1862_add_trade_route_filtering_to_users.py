"""add trade_route_filtering to users

Revision ID: 02c1fbcf1862
Revises: 2a7fce6a77c3
Create Date: 2026-06-17 18:55:32.516981

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '02c1fbcf1862'
down_revision: Union[str, None] = '2a7fce6a77c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column(
        'trade_route_filtering',
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=False,
        server_default='{"buy_orders_only": false}',
    ))


def downgrade() -> None:
    op.drop_column('users', 'trade_route_filtering')
