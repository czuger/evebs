"""Integration test for migration 0011 (blueprint PK refactor).

Creates a minimal pre-migration schema in an isolated PostgreSQL schema,
runs the migration SQL, and verifies the post-migration state.
The test schema is dropped on teardown so it never affects other tests.
"""
import pytest
from sqlalchemy import inspect as sa_inspect, text

from evebs.extensions import db

_S = 'mig_test_0011'

# Mirrors 0011_blueprint_refactor.py — run with search_path set to _S
_UPGRADE_STEPS = [
    "ALTER TABLE blueprints RENAME COLUMN produced_cpp_type_id TO produced_type_id",
    "ALTER TABLE blueprint_materials RENAME COLUMN eve_item_id TO universe_type_id",
    "ALTER TABLE blueprints ALTER COLUMN produced_type_id TYPE BIGINT",
    "ALTER TABLE blueprint_materials ALTER COLUMN id TYPE BIGINT",
    "ALTER TABLE blueprint_materials ALTER COLUMN blueprint_id TYPE BIGINT",
    "ALTER TABLE blueprint_materials ALTER COLUMN required_qtt TYPE BIGINT",
    "ALTER TABLE blueprint_materials DROP CONSTRAINT blueprint_materials_blueprint_id_fkey",
    "ALTER TABLE blueprint_modifications DROP CONSTRAINT blueprint_modifications_blueprint_id_fkey",
    "ALTER TABLE eve_items DROP CONSTRAINT eve_items_blueprint_id_fkey",
    "ALTER TABLE blueprints ADD COLUMN new_id BIGINT",
    "UPDATE blueprints SET new_id = cpp_blueprint_id",
    "ALTER TABLE blueprint_materials ADD COLUMN new_blueprint_id BIGINT",
    "UPDATE blueprint_materials SET new_blueprint_id = b.new_id FROM blueprints b WHERE blueprint_materials.blueprint_id = b.id",
    "ALTER TABLE blueprint_modifications ADD COLUMN new_blueprint_id BIGINT",
    "UPDATE blueprint_modifications SET new_blueprint_id = b.new_id FROM blueprints b WHERE blueprint_modifications.blueprint_id = b.id",
    "ALTER TABLE eve_items ADD COLUMN new_blueprint_id BIGINT",
    "UPDATE eve_items SET new_blueprint_id = b.new_id FROM blueprints b WHERE eve_items.blueprint_id = b.id",
    "ALTER TABLE blueprints DROP CONSTRAINT blueprints_pkey",
    "ALTER TABLE blueprints DROP COLUMN id",
    "ALTER TABLE blueprints DROP COLUMN cpp_blueprint_id",
    "ALTER TABLE blueprints RENAME COLUMN new_id TO id",
    "ALTER TABLE blueprints ADD PRIMARY KEY (id)",
    "ALTER TABLE blueprint_materials DROP COLUMN blueprint_id",
    "ALTER TABLE blueprint_materials RENAME COLUMN new_blueprint_id TO blueprint_id",
    "ALTER TABLE blueprint_materials ALTER COLUMN blueprint_id SET NOT NULL",
    "ALTER TABLE blueprint_materials ADD CONSTRAINT blueprint_materials_blueprint_id_fkey FOREIGN KEY (blueprint_id) REFERENCES blueprints(id)",
    "ALTER TABLE blueprint_modifications DROP COLUMN blueprint_id",
    "ALTER TABLE blueprint_modifications RENAME COLUMN new_blueprint_id TO blueprint_id",
    "ALTER TABLE blueprint_modifications ALTER COLUMN blueprint_id SET NOT NULL",
    "ALTER TABLE blueprint_modifications ADD CONSTRAINT blueprint_modifications_blueprint_id_fkey FOREIGN KEY (blueprint_id) REFERENCES blueprints(id)",
    "ALTER TABLE eve_items DROP COLUMN blueprint_id",
    "ALTER TABLE eve_items RENAME COLUMN new_blueprint_id TO blueprint_id",
    "ALTER TABLE eve_items ADD CONSTRAINT eve_items_blueprint_id_fkey FOREIGN KEY (blueprint_id) REFERENCES blueprints(id)",
]


@pytest.fixture
def migration_schema(app):
    """Create an isolated schema before the test, drop it after."""
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute(text(f"DROP SCHEMA IF EXISTS {_S} CASCADE"))
            conn.execute(text(f"CREATE SCHEMA {_S}"))
            conn.commit()
    yield
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute(text(f"DROP SCHEMA IF EXISTS {_S} CASCADE"))
            conn.commit()


def test_migration_0011_with_eve_items_fk(app, migration_schema):
    """Migration must complete even when eve_items.blueprint_id FK exists."""
    with app.app_context():

        # ---- pre-migration schema (fully qualified names, no search_path needed) ----
        with db.engine.connect() as conn:
            conn.execute(text(f"""
                CREATE TABLE {_S}.blueprints (
                    id SERIAL PRIMARY KEY,
                    cpp_blueprint_id BIGINT NOT NULL UNIQUE,
                    produced_cpp_type_id BIGINT,
                    name VARCHAR NOT NULL DEFAULT '',
                    nb_runs INTEGER NOT NULL DEFAULT 1,
                    prod_qtt INTEGER NOT NULL DEFAULT 1
                )
            """))
            conn.execute(text(f"""
                CREATE TABLE {_S}.blueprint_materials (
                    id SERIAL PRIMARY KEY,
                    blueprint_id INTEGER NOT NULL
                        CONSTRAINT blueprint_materials_blueprint_id_fkey
                        REFERENCES {_S}.blueprints(id),
                    eve_item_id BIGINT NOT NULL,
                    required_qtt INTEGER NOT NULL
                )
            """))
            conn.execute(text(f"""
                CREATE TABLE {_S}.blueprint_modifications (
                    id SERIAL PRIMARY KEY,
                    blueprint_id INTEGER NOT NULL
                        CONSTRAINT blueprint_modifications_blueprint_id_fkey
                        REFERENCES {_S}.blueprints(id),
                    user_id INTEGER,
                    percent_modification_value FLOAT
                )
            """))
            conn.execute(text(f"""
                CREATE TABLE {_S}.eve_items (
                    id SERIAL PRIMARY KEY,
                    blueprint_id INTEGER
                        CONSTRAINT eve_items_blueprint_id_fkey
                        REFERENCES {_S}.blueprints(id)
                )
            """))
            # surrogate id=1 maps to natural cpp_blueprint_id=681
            conn.execute(text(f"INSERT INTO {_S}.blueprints (id, cpp_blueprint_id, produced_cpp_type_id, name) VALUES (1, 681, 165, 'Tritanium BP')"))
            conn.execute(text(f"INSERT INTO {_S}.blueprint_materials (blueprint_id, eve_item_id, required_qtt) VALUES (1, 38, 86)"))
            conn.execute(text(f"INSERT INTO {_S}.blueprint_modifications (blueprint_id, user_id) VALUES (1, 99)"))
            conn.execute(text(f"INSERT INTO {_S}.eve_items (id, blueprint_id) VALUES (100, 1), (200, NULL)"))
            conn.commit()

        # ---- run migration (unqualified names → need search_path) ----
        with db.engine.connect() as conn:
            conn.execute(text(f"SET search_path TO {_S}"))
            for step in _UPGRADE_STEPS:
                conn.execute(text(step))
            conn.execute(text("RESET search_path"))
            conn.commit()

        # ---- verify post-migration state ----
        with db.engine.connect() as conn:
            bp_cols = {c['name'] for c in sa_inspect(conn).get_columns('blueprints', schema=_S)}
            assert 'id' in bp_cols
            assert 'produced_type_id' in bp_cols
            assert 'produced_cpp_type_id' not in bp_cols
            assert 'cpp_blueprint_id' not in bp_cols

            mat_cols = {c['name'] for c in sa_inspect(conn).get_columns('blueprint_materials', schema=_S)}
            assert 'universe_type_id' in mat_cols
            assert 'eve_item_id' not in mat_cols

            # natural PK: row is now keyed by 681 (was cpp_blueprint_id)
            row = conn.execute(text(f"SELECT id, produced_type_id FROM {_S}.blueprints")).first()
            assert row.id == 681
            assert row.produced_type_id == 165

            # eve_items.blueprint_id remapped: surrogate 1 → natural 681
            linked = conn.execute(text(f"SELECT blueprint_id FROM {_S}.eve_items WHERE id = 100")).first()
            assert linked.blueprint_id == 681

            null_row = conn.execute(text(f"SELECT blueprint_id FROM {_S}.eve_items WHERE id = 200")).first()
            assert null_row.blueprint_id is None

            # FK is live: a bad reference must fail
            with pytest.raises(Exception, match='violates foreign key'):
                conn.execute(text(f"INSERT INTO {_S}.eve_items (id, blueprint_id) VALUES (999, 9999)"))
