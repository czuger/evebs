"""add industry_facilities table and drop industry_costs_indices from universe_stations

Revision ID: 0014_industry_facilities
Revises: 0013_user_location_routing
Create Date: 2026-05-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0014_industry_facilities'
down_revision = '0013_user_location_routing'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'industry_facilities',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column('universe_system_id', sa.BigInteger(),
                  sa.ForeignKey('universe_systems.id'), nullable=False),
        sa.Column('universe_station_id', sa.BigInteger(),
                  sa.ForeignKey('universe_stations.id'), nullable=True),
        sa.Column('owner_id', sa.BigInteger(), nullable=False),
        sa.Column('type_id', sa.BigInteger(), nullable=False),
        sa.Column('tax', sa.Float(), nullable=True),
    )
    op.drop_column('universe_stations', 'industry_costs_indices')


def downgrade():
    op.drop_table('industry_facilities')
    op.add_column('universe_stations',
                  sa.Column('industry_costs_indices',
                            postgresql.JSON(astext_type=sa.Text()), nullable=True))
