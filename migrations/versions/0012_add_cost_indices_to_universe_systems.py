"""add cost_indices to universe_systems

Revision ID: 0012_add_cost_indices
Revises: 0011_blueprint_refactor
Create Date: 2026-05-18

"""
from alembic import op
import sqlalchemy as sa

revision = '0012_add_cost_indices'
down_revision = '0011_blueprint_refactor'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('universe_systems',
                  sa.Column('cost_indices', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('universe_systems', 'cost_indices')
