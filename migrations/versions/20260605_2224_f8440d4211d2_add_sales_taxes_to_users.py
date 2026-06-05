"""add sales_taxes to users

Revision ID: f8440d4211d2
Revises: 0f8b44b4b0b0
Create Date: 2026-06-05 22:24:05.314331

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f8440d4211d2'
down_revision: Union[str, None] = '0f8b44b4b0b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column(
        'sales_taxes',
        sa.JSON(),
        nullable=False,
        server_default='{"broker_fee_taxes": 2, "sales_taxes": 4, "safety_tax": 0}',
    ))


def downgrade() -> None:
    op.drop_column('users', 'sales_taxes')
