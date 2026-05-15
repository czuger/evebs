"""add unique constraints for upserts

Revision ID: b3f2a1c9d4e7
Revises: 1858046133a8
Create Date: 2026-05-15

"""
from alembic import op

revision = 'b3f2a1c9d4e7'
down_revision = '1858046133a8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint('uq_prices_mins_hub_item', 'prices_mins', ['trade_hub_id', 'eve_item_id'])
    op.create_unique_constraint('uq_buy_orders_analytics_hub_item', 'buy_orders_analytics', ['trade_hub_id', 'eve_item_id'])
    op.create_unique_constraint('uq_weekly_price_details_item_hub_day', 'weekly_price_details', ['eve_item_id', 'trade_hub_id', 'day'])
    op.create_unique_constraint('uq_prices_advices_item_hub', 'prices_advices', ['eve_item_id', 'trade_hub_id'])


def downgrade():
    op.drop_constraint('uq_prices_advices_item_hub', 'prices_advices', type_='unique')
    op.drop_constraint('uq_weekly_price_details_item_hub_day', 'weekly_price_details', type_='unique')
    op.drop_constraint('uq_buy_orders_analytics_hub_item', 'buy_orders_analytics', type_='unique')
    op.drop_constraint('uq_prices_mins_hub_item', 'prices_mins', type_='unique')
