"""Drop the legacy regions table.

Revision ID: h2i3j4k5l6m7
Revises: g1h2i3j4k5l6
Create Date: 2026-06-01
"""
from __future__ import annotations
from typing import Union

from alembic import op

revision: str = 'h2i3j4k5l6m7'
down_revision: Union[str, None] = 'g1h2i3j4k5l6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table('regions')


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
