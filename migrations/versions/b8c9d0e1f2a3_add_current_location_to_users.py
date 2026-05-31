"""Add current_location_station_id to users

Revision ID: b8c9d0e1f2a3
Revises: e6f7a8b9c0d1
Create Date: 2026-05-31

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b8c9d0e1f2a3'
down_revision: Union[str, None] = 'e6f7a8b9c0d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('current_location_station_id', sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'current_location_station_id')
