"""rename industry_taxes to industry_modifications

Revision ID: 0a8f7147cc87
Revises: 7712d16b56e7
Create Date: 2026-06-20 06:33:29.356152

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0a8f7147cc87'
down_revision: Union[str, None] = '7712d16b56e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL auto-updates the user_industry_costs view's column references on rename.
    op.alter_column('users', 'industry_taxes', new_column_name='industry_modifications')


def downgrade() -> None:
    op.alter_column('users', 'industry_modifications', new_column_name='industry_taxes')
