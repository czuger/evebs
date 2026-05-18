"""add facility_tax and scc_surcharge to users

Revision ID: 0015_user_facility_tax_scc
Revises: 0014_industry_facilities
Create Date: 2026-05-18

"""
from alembic import op
import sqlalchemy as sa

revision = '0015_user_facility_tax_scc'
down_revision = '0014_industry_facilities'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('facility_tax', sa.Float(), nullable=False, server_default='0.25'))
    op.add_column('users', sa.Column('scc_surcharge', sa.Float(), nullable=False, server_default='4.0'))


def downgrade():
    op.drop_column('users', 'scc_surcharge')
    op.drop_column('users', 'facility_tax')
