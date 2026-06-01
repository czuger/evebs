"""Added account table

Revision ID: 9bf5fd36f1ed
Revises: k5l6m7n8o9p0
Create Date: 2026-06-01 07:16:37.539923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9bf5fd36f1ed'
down_revision: Union[str, None] = 'k5l6m7n8o9p0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
