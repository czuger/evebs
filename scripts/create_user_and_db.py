#!/usr/bin/env python3
"""
Create the PostgreSQL user (if missing) and database, then initialise the schema.

Admin credentials are read from config/config.json under database.admin_user /
database.admin_password (defaults: postgres / '').

Usage:
  python scripts/create_user_and_db.py
  python scripts/create_user_and_db.py --recreate   # drop + recreate schema
  python scripts/create_user_and_db.py --test        # use test database (*_test)
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg
from psycopg import sql

parser = argparse.ArgumentParser(description="Create DB user/database and initialise schema.")
parser.add_argument(
    "-r", "--recreate",
    action="store_true",
    help="Drop all tables and views, then recreate from scratch.",
)
parser.add_argument(
    "-t", "--test",
    action="store_true",
    help="Use the test database (*_test suffix).",
)
args = parser.parse_args()

if args.test:
    os.environ['EVEBS_TEST_DB'] = '1'

from config import Config, _cfg, _test_mode

db_cfg      = _cfg.get('database', {})
host        = db_cfg.get('host')
port        = db_cfg.get('port', 5432)
db_user     = db_cfg.get('user', '')
db_password = db_cfg.get('password', '')
db_name     = db_cfg.get('name', '')
if _test_mode:
    db_name = f'{db_name}_test'

admin_user     = db_cfg.get('admin_user', 'postgres')
admin_password = db_cfg.get('admin_password', '')

if host:
    # --- PostgreSQL: create user + database via superuser connection -----------
    print(f"Connecting to PostgreSQL as '{admin_user}' on {host}:{port}…")
    with psycopg.connect(
        host=host, port=port, dbname='postgres',
        user=admin_user, password=admin_password,
        autocommit=True,
    ) as conn:
        with conn.cursor() as cur:
            # Create user if not exists
            cur.execute(
                "SELECT 1 FROM pg_roles WHERE rolname = %s", (db_user,)
            )
            if cur.fetchone() is None:
                cur.execute(
                    sql.SQL("CREATE USER {} WITH PASSWORD {}").format(
                        sql.Identifier(db_user),
                        sql.Literal(db_password),
                    )
                )
                print(f"  User '{db_user}' created.")
            else:
                print(f"  User '{db_user}' already exists.")

            # Create database if not exists
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
            )
            if cur.fetchone() is None:
                cur.execute(
                    f'CREATE DATABASE "{db_name}" OWNER {db_user}'
                )
                print(f"  Database '{db_name}' created.")
            else:
                print(f"  Database '{db_name}' already exists.")

            cur.execute(
                f'GRANT ALL PRIVILEGES ON DATABASE "{db_name}" TO {db_user}'
            )

from alembic.config import Config as AlembicConfig
from alembic import command

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ['ALEMBIC_DB_URL'] = Config.SQLALCHEMY_DATABASE_URI

alembic_cfg = AlembicConfig(os.path.join(_project_root, 'alembic.ini'))
alembic_cfg.set_main_option('script_location', os.path.join(_project_root, 'migrations'))

if args.recreate:
    print("Dropping and recreating public schema…")
    with psycopg.connect(
        host=host, port=port, dbname=db_name,
        user=admin_user, password=admin_password,
    ) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA public CASCADE")
            cur.execute("CREATE SCHEMA public")
            cur.execute(sql.SQL("GRANT ALL ON SCHEMA public TO {}").format(sql.Identifier(db_user)))
            cur.execute("GRANT ALL ON SCHEMA public TO public")
    print("  Schema dropped and recreated.")

print("Upgrading to head…")
command.upgrade(alembic_cfg, 'head')
print("Done.")
