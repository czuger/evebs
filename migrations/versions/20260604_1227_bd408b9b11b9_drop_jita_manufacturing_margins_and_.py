"""drop jita_manufacturing_margins and jita_reaction_margins views

Revision ID: bd408b9b11b9
Revises: e5c53edc37ef
Create Date: 2026-06-04 12:27:19.454224

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'bd408b9b11b9'
down_revision: Union[str, None] = 'e5c53edc37ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text('DROP MATERIALIZED VIEW IF EXISTS jita_manufacturing_margins'))
    conn.execute(sa.text('DROP MATERIALIZED VIEW IF EXISTS jita_reaction_margins'))


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
