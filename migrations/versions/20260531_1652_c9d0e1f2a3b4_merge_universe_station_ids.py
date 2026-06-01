"""Merge universe_station id and cpp_station_id — use Eve station ID as PK.

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-05-31
"""
from __future__ import annotations
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = 'c9d0e1f2a3b4'
down_revision: Union[str, None] = 'b8c9d0e1f2a3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Drop FK constraints first so updates aren't blocked by referential integrity checks
    conn.execute(sa.text(
        'ALTER TABLE bpc_assets DROP CONSTRAINT bpc_assets_universe_station_id_fkey'
    ))
    conn.execute(sa.text(
        'ALTER TABLE bpc_assets_stations DROP CONSTRAINT bpc_assets_stations_universe_station_id_fkey'
    ))
    conn.execute(sa.text(
        'ALTER TABLE users DROP CONSTRAINT users_selected_assets_station_id_fkey'
    ))

    # 2. Remap FK columns in dependent tables to the Eve station ID (cpp_station_id)
    conn.execute(sa.text('''
        UPDATE bpc_assets SET universe_station_id = s.cpp_station_id
        FROM universe_stations s WHERE bpc_assets.universe_station_id = s.id
    '''))
    conn.execute(sa.text('''
        UPDATE bpc_assets_stations SET universe_station_id = s.cpp_station_id
        FROM universe_stations s WHERE bpc_assets_stations.universe_station_id = s.id
    '''))
    conn.execute(sa.text('''
        UPDATE users SET selected_assets_station_id = s.cpp_station_id
        FROM universe_stations s WHERE users.selected_assets_station_id = s.id
    '''))
    conn.execute(sa.text('''
        UPDATE users SET current_location_station_id = s.cpp_station_id
        FROM universe_stations s WHERE users.current_location_station_id = s.id
    '''))

    # 3. Drop PK and unique constraint on universe_stations
    conn.execute(sa.text(
        'ALTER TABLE universe_stations DROP CONSTRAINT universe_stations_pkey'
    ))
    conn.execute(sa.text(
        'ALTER TABLE universe_stations DROP CONSTRAINT universe_stations_cpp_station_id_key'
    ))

    # 4. Drop old auto-increment id column
    conn.execute(sa.text('ALTER TABLE universe_stations DROP COLUMN id'))

    # 5. Rename cpp_station_id → id and widen to bigint
    conn.execute(sa.text(
        'ALTER TABLE universe_stations RENAME COLUMN cpp_station_id TO id'
    ))
    conn.execute(sa.text(
        'ALTER TABLE universe_stations ALTER COLUMN id TYPE BIGINT'
    ))

    # 6. Add new primary key
    conn.execute(sa.text(
        'ALTER TABLE universe_stations ADD CONSTRAINT universe_stations_pkey PRIMARY KEY (id)'
    ))

    # 7. Re-add FK constraints
    conn.execute(sa.text(
        'ALTER TABLE bpc_assets ADD CONSTRAINT bpc_assets_universe_station_id_fkey '
        'FOREIGN KEY (universe_station_id) REFERENCES universe_stations(id)'
    ))
    conn.execute(sa.text(
        'ALTER TABLE bpc_assets_stations ADD CONSTRAINT bpc_assets_stations_universe_station_id_fkey '
        'FOREIGN KEY (universe_station_id) REFERENCES universe_stations(id)'
    ))
    conn.execute(sa.text(
        'ALTER TABLE users ADD CONSTRAINT users_selected_assets_station_id_fkey '
        'FOREIGN KEY (selected_assets_station_id) REFERENCES universe_stations(id)'
    ))


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
