"""add manufacturing_tree json column to blueprints

Revision ID: ed2f10479334
Revises: 36d771e4f49c
Create Date: 2026-06-03 22:59:57.144875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'ed2f10479334'
down_revision: Union[str, None] = '36d771e4f49c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().execute(sa.text(
        'ALTER TABLE blueprints ADD COLUMN manufacturing_tree JSONB'
    ))


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
