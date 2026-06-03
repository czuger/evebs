"""add esi_item_id, parent_esi_item_id, is_blueprint_copy to bpc_assets

Revision ID: a0e132bfde89
Revises: 62fdbc42a071
Create Date: 2026-06-03 10:09:49.271112

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a0e132bfde89'
down_revision: Union[str, None] = '62fdbc42a071'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('bpc_assets', sa.Column('esi_item_id', sa.BigInteger(), nullable=True))
    op.add_column('bpc_assets', sa.Column('parent_esi_item_id', sa.BigInteger(), nullable=True))
    op.add_column('bpc_assets', sa.Column('is_blueprint_copy', sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column('bpc_assets', 'is_blueprint_copy')
    op.drop_column('bpc_assets', 'parent_esi_item_id')
    op.drop_column('bpc_assets', 'esi_item_id')
