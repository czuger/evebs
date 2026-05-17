"""create market_prices table

Revision ID: 0008_create_market_prices
Revises: 0007_migrate_eve_item_fks
Create Date: 2026-05-18

"""
from alembic import op
import sqlalchemy as sa

revision = '0008_create_market_prices'
down_revision = '0007_migrate_eve_item_fks'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('DROP TABLE IF EXISTS market_prices')
    op.create_table(
        'market_prices',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('type_id', sa.BigInteger(), nullable=False),
        sa.Column('adjusted_price', sa.Float(), nullable=True),
        sa.Column('average_price', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['type_id'], ['universe_types.id']),
    )
    op.create_index('ix_market_prices_type_id', 'market_prices', ['type_id'], unique=True)


def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_market_prices_type_id")
    op.drop_table('market_prices')
