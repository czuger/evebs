"""migrate universe cpp_* fields to BigInteger

Revision ID: 0002_universe_cpp_fields_to_bigint
Revises: 0001_initial_schema
Create Date: 2026-05-16

"""
from alembic import op
import sqlalchemy as sa

revision = '0002_universe_cpp_fields_to_bigint'
down_revision = '0001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('universe_regions', 'cpp_region_id',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    existing_nullable=False)

    op.alter_column('universe_constellations', 'cpp_constellation_id',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    existing_nullable=False)

    op.alter_column('universe_systems', 'cpp_system_id',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    existing_nullable=False)

    op.alter_column('universe_systems', 'cpp_star_id',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    existing_nullable=False)


def downgrade():
    op.alter_column('universe_systems', 'cpp_star_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.Integer(),
                    existing_nullable=False)

    op.alter_column('universe_systems', 'cpp_system_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.Integer(),
                    existing_nullable=False)

    op.alter_column('universe_constellations', 'cpp_constellation_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.Integer(),
                    existing_nullable=False)

    op.alter_column('universe_regions', 'cpp_region_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.Integer(),
                    existing_nullable=False)
