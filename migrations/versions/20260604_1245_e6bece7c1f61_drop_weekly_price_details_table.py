"""drop weekly_price_details table

Revision ID: e6bece7c1f61
Revises: 9bae17e1326f
Create Date: 2026-06-04 12:45:24.870321

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e6bece7c1f61'
down_revision: Union[str, None] = '9bae17e1326f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().execute(sa.text('DROP TABLE IF EXISTS weekly_price_details'))


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
