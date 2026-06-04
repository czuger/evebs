"""drop jita_prices materialized view

Revision ID: 9bae17e1326f
Revises: bd408b9b11b9
Create Date: 2026-06-04 12:43:12.218350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9bae17e1326f'
down_revision: Union[str, None] = 'bd408b9b11b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().execute(sa.text('DROP MATERIALIZED VIEW IF EXISTS jita_prices'))


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
