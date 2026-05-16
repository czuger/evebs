"""remove cpp_ prefix from universe models — collapse cpp_*_id into id

Revision ID: 0003_remove_cpp_prefix_from_universe_models
Revises: 0002_universe_cpp_fields_to_bigint
Create Date: 2026-05-16

"""
from alembic import op

revision = '0003_universe_no_cpp'
down_revision = '0002_universe_bigint'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Drop all FK constraints referencing universe tables
    op.drop_constraint('universe_constellations_universe_region_id_fkey', 'universe_constellations', type_='foreignkey')
    op.drop_constraint('universe_systems_universe_constellation_id_fkey', 'universe_systems', type_='foreignkey')
    op.drop_constraint('universe_stations_universe_system_id_fkey', 'universe_stations', type_='foreignkey')
    op.drop_constraint('trade_hubs_region_id_fkey', 'trade_hubs', type_='foreignkey')
    op.drop_constraint('eve_market_histories_groups_universe_region_id_fkey', 'eve_market_histories_groups', type_='foreignkey')
    op.drop_constraint('structures_universe_system_id_fkey', 'structures', type_='foreignkey')
    op.drop_constraint('bpc_assets_universe_station_id_fkey', 'bpc_assets', type_='foreignkey')
    op.drop_constraint('bpc_assets_stations_universe_station_id_fkey', 'bpc_assets_stations', type_='foreignkey')
    op.drop_constraint('users_selected_assets_station_id_fkey', 'users', type_='foreignkey')

    # Step 2: Rewrite FK columns in all child tables to use CPP IDs
    op.execute("""
        UPDATE universe_constellations c
        SET universe_region_id = r.cpp_region_id
        FROM universe_regions r
        WHERE c.universe_region_id = r.id
    """)
    op.execute("""
        UPDATE universe_systems s
        SET universe_constellation_id = c.cpp_constellation_id
        FROM universe_constellations c
        WHERE s.universe_constellation_id = c.id
    """)
    op.execute("""
        UPDATE universe_stations st
        SET universe_system_id = sy.cpp_system_id
        FROM universe_systems sy
        WHERE st.universe_system_id = sy.id
    """)
    op.execute("""
        UPDATE trade_hubs t
        SET region_id = r.cpp_region_id
        FROM universe_regions r
        WHERE t.region_id = r.id
    """)
    op.execute("""
        UPDATE eve_market_histories_groups h
        SET universe_region_id = r.cpp_region_id
        FROM universe_regions r
        WHERE h.universe_region_id = r.id
    """)
    op.execute("""
        UPDATE structures s
        SET universe_system_id = sy.cpp_system_id
        FROM universe_systems sy
        WHERE s.universe_system_id = sy.id
    """)
    op.execute("""
        UPDATE bpc_assets a
        SET universe_station_id = st.cpp_station_id
        FROM universe_stations st
        WHERE a.universe_station_id = st.id
    """)
    op.execute("""
        UPDATE bpc_assets_stations a
        SET universe_station_id = st.cpp_station_id
        FROM universe_stations st
        WHERE a.universe_station_id = st.id
    """)
    op.execute("""
        UPDATE users u
        SET selected_assets_station_id = st.cpp_station_id
        FROM universe_stations st
        WHERE u.selected_assets_station_id = st.id
    """)

    # Step 3: Restructure universe_regions — cpp_region_id becomes id
    op.execute('ALTER TABLE universe_regions DROP CONSTRAINT universe_regions_pkey CASCADE')
    op.execute('ALTER TABLE universe_regions DROP COLUMN id')
    op.drop_constraint('universe_regions_cpp_region_id_key', 'universe_regions', type_='unique')
    op.execute('ALTER TABLE universe_regions RENAME COLUMN cpp_region_id TO id')
    op.execute('ALTER TABLE universe_regions ADD PRIMARY KEY (id)')

    # Step 4: Restructure universe_constellations — cpp_constellation_id becomes id
    op.execute('ALTER TABLE universe_constellations DROP CONSTRAINT universe_constellations_pkey CASCADE')
    op.execute('ALTER TABLE universe_constellations DROP COLUMN id')
    op.drop_constraint('universe_constellations_cpp_constellation_id_key', 'universe_constellations', type_='unique')
    op.execute('ALTER TABLE universe_constellations RENAME COLUMN cpp_constellation_id TO id')
    op.execute('ALTER TABLE universe_constellations ADD PRIMARY KEY (id)')

    # Step 5: Restructure universe_systems — cpp_system_id becomes id, cpp_star_id → star_id
    op.execute('ALTER TABLE universe_systems DROP CONSTRAINT universe_systems_pkey CASCADE')
    op.execute('ALTER TABLE universe_systems DROP COLUMN id')
    op.drop_constraint('universe_systems_cpp_system_id_key', 'universe_systems', type_='unique')
    op.execute('ALTER TABLE universe_systems RENAME COLUMN cpp_system_id TO id')
    op.execute('ALTER TABLE universe_systems ADD PRIMARY KEY (id)')
    op.execute('ALTER TABLE universe_systems RENAME COLUMN cpp_star_id TO star_id')

    # Step 6: Restructure universe_stations — cpp_station_id becomes id, cpp_owner_id → owner_id
    op.execute('ALTER TABLE universe_stations DROP CONSTRAINT universe_stations_pkey CASCADE')
    op.execute('ALTER TABLE universe_stations DROP COLUMN id')
    op.drop_constraint('universe_stations_cpp_station_id_key', 'universe_stations', type_='unique')
    op.execute('ALTER TABLE universe_stations RENAME COLUMN cpp_station_id TO id')
    op.execute('ALTER TABLE universe_stations ADD PRIMARY KEY (id)')
    op.execute('ALTER TABLE universe_stations RENAME COLUMN cpp_owner_id TO owner_id')

    # Step 7: Re-add all FK constraints
    op.create_foreign_key(
        'universe_constellations_universe_region_id_fkey',
        'universe_constellations', 'universe_regions',
        ['universe_region_id'], ['id'],
    )
    op.create_foreign_key(
        'universe_systems_universe_constellation_id_fkey',
        'universe_systems', 'universe_constellations',
        ['universe_constellation_id'], ['id'],
    )
    op.create_foreign_key(
        'universe_stations_universe_system_id_fkey',
        'universe_stations', 'universe_systems',
        ['universe_system_id'], ['id'],
    )
    op.create_foreign_key(
        'trade_hubs_region_id_fkey',
        'trade_hubs', 'universe_regions',
        ['region_id'], ['id'],
    )
    op.create_foreign_key(
        'eve_market_histories_groups_universe_region_id_fkey',
        'eve_market_histories_groups', 'universe_regions',
        ['universe_region_id'], ['id'],
    )
    op.create_foreign_key(
        'structures_universe_system_id_fkey',
        'structures', 'universe_systems',
        ['universe_system_id'], ['id'],
    )
    op.create_foreign_key(
        'bpc_assets_universe_station_id_fkey',
        'bpc_assets', 'universe_stations',
        ['universe_station_id'], ['id'],
    )
    op.create_foreign_key(
        'bpc_assets_stations_universe_station_id_fkey',
        'bpc_assets_stations', 'universe_stations',
        ['universe_station_id'], ['id'],
    )
    op.create_foreign_key(
        'users_selected_assets_station_id_fkey',
        'users', 'universe_stations',
        ['selected_assets_station_id'], ['id'],
    )


def downgrade():
    raise NotImplementedError('Downgrade not supported for this migration')
