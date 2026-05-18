"""add stargates to universe_systems

Revision ID: 0009_add_stargates
Revises: 0008_create_market_prices
Create Date: 2026-05-18

"""
from alembic import op
import sqlalchemy as sa

revision = '0009_add_stargates'
down_revision = '0008_create_market_prices'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('universe_systems', sa.Column('stargates', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('universe_systems', 'stargates')
