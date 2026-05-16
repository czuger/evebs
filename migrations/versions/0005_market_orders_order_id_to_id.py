"""rename market_orders.order_id to id

Revision ID: 0005_market_orders_id
Revises: 0004_new_models
Create Date: 2026-05-16

"""
from alembic import op

revision = '0005_market_orders_id'
down_revision = '0004_new_models'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE market_orders DROP CONSTRAINT market_orders_pkey CASCADE')
    op.execute('ALTER TABLE market_orders RENAME COLUMN order_id TO id')
    op.execute('ALTER TABLE market_orders ADD PRIMARY KEY (id)')


def downgrade():
    raise NotImplementedError('Downgrade not supported for this migration')
