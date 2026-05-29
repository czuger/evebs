"""Add analytics lookup index on public_trade_orders

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-05-29

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite has no INCLUDE clause; volume_remain is added as a key column for covering index behaviour
    op.create_index(
        'idx_public_trade_orders_analytics_lookup',
        'public_trade_orders',
        ['trade_hub_id', 'eve_item_id', 'is_buy_order', 'price', 'volume_remain'],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index('idx_public_trade_orders_analytics_lookup', table_name='public_trade_orders', if_exists=True)
