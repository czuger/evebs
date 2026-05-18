"""add industry_interesting_items table

Revision ID: 0016_industry_interesting_items
Revises: 0015_user_facility_tax_scc
Create Date: 2026-05-18

"""
from alembic import op
import sqlalchemy as sa

revision = '0016_industry_interesting_items'
down_revision = '0015_user_facility_tax_scc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'industry_interesting_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('region_id', sa.BigInteger(), sa.ForeignKey('universe_regions.id'), nullable=False),
        sa.Column('item_id', sa.BigInteger(), sa.ForeignKey('universe_types.id'), nullable=False),
        sa.UniqueConstraint('region_id', 'item_id', name='uq_industry_interesting_items_region_item'),
    )


def downgrade():
    op.drop_table('industry_interesting_items')
