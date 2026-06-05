"""Add is_potential and potential_type to bpc_assets

Revision ID: cb2263e81cf3
Revises: e6bece7c1f61
Create Date: 2026-06-04 17:25:19.157811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'cb2263e81cf3'
down_revision: Union[str, None] = 'e6bece7c1f61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('bpc_assets', sa.Column('is_potential', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('bpc_assets', sa.Column('potential_type', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('bpc_assets', 'potential_type')
    op.drop_column('bpc_assets', 'is_potential')
