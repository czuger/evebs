"""weekly_price_details unique constraint on (eve_item_id, trade_hub_id, day)

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-25

"""
from alembic import op

revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        'uq_weekly_price_details_item_hub_day',
        'weekly_price_details',
        ['eve_item_id', 'trade_hub_id', 'day'],
    )


def downgrade():
    op.drop_constraint(
        'uq_weekly_price_details_item_hub_day',
        'weekly_price_details',
        type_='unique',
    )
