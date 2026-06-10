"""rename bpc_assets to user_assets

Revision ID: 883b8b583df6
Revises: 450b44c06b76
Create Date: 2026-06-10 18:41:10.817465

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '883b8b583df6'
down_revision: Union[str, None] = '450b44c06b76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('bpc_assets', 'user_assets')


def downgrade() -> None:
    op.rename_table('user_assets', 'bpc_assets')
