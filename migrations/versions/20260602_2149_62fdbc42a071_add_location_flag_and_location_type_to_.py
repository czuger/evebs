"""add location_flag and location_type to bpc_assets

Revision ID: 62fdbc42a071
Revises: 078a83111fd8
Create Date: 2026-06-02 21:49:58.819535

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '62fdbc42a071'
down_revision: Union[str, None] = '078a83111fd8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('bpc_assets', sa.Column('location_flag', sa.String(), nullable=True))
    op.add_column('bpc_assets', sa.Column('location_type', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('bpc_assets', 'location_type')
    op.drop_column('bpc_assets', 'location_flag')
