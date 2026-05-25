"""Add unique constraints required by upsert queries on prices_mins, buy_orders_analytics, prices_advices

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-25

"""
from alembic import op

revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        'uq_prices_mins_hub_item', 'prices_mins', ['trade_hub_id', 'eve_item_id']
    )
    op.create_unique_constraint(
        'uq_buy_orders_analytics_hub_item', 'buy_orders_analytics', ['trade_hub_id', 'eve_item_id']
    )
    op.create_unique_constraint(
        'uq_prices_advices_item_hub', 'prices_advices', ['eve_item_id', 'trade_hub_id']
    )


def downgrade():
    op.drop_constraint('uq_prices_advices_item_hub', 'prices_advices', type_='unique')
    op.drop_constraint('uq_buy_orders_analytics_hub_item', 'buy_orders_analytics', type_='unique')
    op.drop_constraint('uq_prices_mins_hub_item', 'prices_mins', type_='unique')
