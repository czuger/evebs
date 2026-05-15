"""remove regions table, reroute trade_hubs.region_id FK to universe_regions

Revision ID: c4e1f2d3a5b6
Revises: b3f2a1c9d4e7
Create Date: 2026-05-15

"""
from alembic import op
import sqlalchemy as sa

revision = 'c4e1f2d3a5b6'
down_revision = 'b3f2a1c9d4e7'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('trade_hubs_region_id_fkey', 'trade_hubs', type_='foreignkey')
    op.alter_column('trade_hubs', 'region_id', type_=sa.BigInteger(), postgresql_using='region_id::bigint')
    op.create_foreign_key(
        'trade_hubs_region_id_fkey', 'trade_hubs',
        'universe_regions', ['region_id'], ['id']
    )
    op.drop_table('regions')


def downgrade():
    op.create_table(
        'regions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cpp_region_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cpp_region_id'),
    )
    op.drop_constraint('trade_hubs_region_id_fkey', 'trade_hubs', type_='foreignkey')
    op.alter_column('trade_hubs', 'region_id', type_=sa.Integer(), postgresql_using='region_id::integer')
    op.create_foreign_key(
        'trade_hubs_region_id_fkey', 'trade_hubs',
        'regions', ['region_id'], ['id']
    )
