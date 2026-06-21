"""add prophet_parameters to eve_items

Revision ID: 24e65aabae4b
Revises: 0a8f7147cc87
Create Date: 2026-06-20 20:33:33.393558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '24e65aabae4b'
down_revision: Union[str, None] = '0a8f7147cc87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('ALTER TABLE eve_items ADD COLUMN prophet_parameters JSONB')
    op.execute('CREATE INDEX ix_eve_items_prophet_parameters '
               'ON eve_items USING gin (prophet_parameters)')


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS ix_eve_items_prophet_parameters')
    op.execute('ALTER TABLE eve_items DROP COLUMN prophet_parameters')
