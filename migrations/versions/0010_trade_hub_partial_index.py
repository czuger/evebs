"""partial index on universe_systems.trade_hub

Revision ID: 0010_trade_hub_idx
Revises: 0009_add_stargates
Create Date: 2026-05-18

"""
from alembic import op

revision = '0010_trade_hub_idx'
down_revision = '0009_add_stargates'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        'CREATE INDEX ix_universe_systems_trade_hub ON universe_systems (trade_hub) WHERE trade_hub = TRUE'
    )


def downgrade():
    op.execute('DROP INDEX IF EXISTS ix_universe_systems_trade_hub')
