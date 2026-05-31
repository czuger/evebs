"""Drop stations table and universe_stations.station_id column.

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-05-31
"""
from __future__ import annotations
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = 'd0e1f2a3b4c5'
down_revision: Union[str, None] = 'c9d0e1f2a3b4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint('universe_stations_station_id_fkey', 'universe_stations', type_='foreignkey')
    op.drop_column('universe_stations', 'station_id')
    op.drop_table('stations')


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
