import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from config import Config
from evebs.extensions import db
import evebs.models  # noqa: F401

alembic_config = context.config

if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

db_url = os.environ.get('ALEMBIC_DB_URL', Config.SQLALCHEMY_DATABASE_URI)
print("db_url =", db_url)
alembic_config.set_main_option('sqlalchemy.url', db_url)

target_metadata = db.metadata


def include_object(obj, name, type_, reflected, compare_to):
    if type_ == 'table':
        table = db.metadata.tables.get(name)
        if table is not None and table.info.get('is_view'):
            return False
    return True


def run_migrations_offline():
    url = alembic_config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        alembic_config.get_section(alembic_config.config_ini_section, {}),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
