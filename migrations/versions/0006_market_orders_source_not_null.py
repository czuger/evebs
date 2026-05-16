"""make market_orders.source not null

Revision ID: 0006_market_orders_source
Revises: 0005_market_orders_id
Create Date: 2026-05-16

"""
from alembic import op
import sqlalchemy as sa

revision = '0006_market_orders_source'
down_revision = '0005_market_orders_id'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('market_orders', 'source',
                    existing_type=sa.Enum('list_order_in_a_region', 'list_order_in_a_structure', name='market_order_source'),
                    nullable=False)


def downgrade():
    op.alter_column('market_orders', 'source',
                    existing_type=sa.Enum('list_order_in_a_region', 'list_order_in_a_structure', name='market_order_source'),
                    nullable=True)
