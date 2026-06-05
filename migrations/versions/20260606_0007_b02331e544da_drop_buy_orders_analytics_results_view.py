"""drop buy_orders_analytics_results view

Revision ID: b02331e544da
Revises: 71bd8c351a17
Create Date: 2026-06-06 00:07:44.211841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b02331e544da'
down_revision: Union[str, None] = '71bd8c351a17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('DROP VIEW IF EXISTS buy_orders_analytics_results')


def downgrade() -> None:
    pass
