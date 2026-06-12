"""drop buy_orders_analytics table

Revision ID: 8f77fa1ce9d9
Revises: 4f8a1166d8d9
Create Date: 2026-06-12 13:38:53.406937

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8f77fa1ce9d9'
down_revision: Union[str, None] = '4f8a1166d8d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.text('DROP TABLE IF EXISTS buy_orders_analytics'))


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
