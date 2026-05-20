"""Replace eve_items table with universe_types, migrating cost/weekly_avg_price/base_item columns

Revision ID: 0019_replace_eve_items
Revises: 0018_drop_public_trade_orders
Create Date: 2026-05-20

"""
from alembic import op

revision = '0019_replace_eve_items'
down_revision = '0018_drop_public_trade_orders'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE universe_types ADD COLUMN IF NOT EXISTS cost DOUBLE PRECISION")
    op.execute("ALTER TABLE universe_types ADD COLUMN IF NOT EXISTS weekly_avg_price DOUBLE PRECISION")
    op.execute("ALTER TABLE universe_types ADD COLUMN IF NOT EXISTS base_item BOOLEAN NOT NULL DEFAULT FALSE")

    op.execute("""
        UPDATE universe_types ut
        SET cost             = ei.cost,
            weekly_avg_price = ei.weekly_avg_price,
            base_item        = COALESCE(ei.base_item, FALSE)
        FROM eve_items ei
        WHERE ut.id = ei.id
    """)

    op.execute("DROP TABLE IF EXISTS eve_items CASCADE")


def downgrade():
    op.execute("""
        CREATE TABLE eve_items (
            id                       SERIAL PRIMARY KEY,
            cpp_eve_item_id          INTEGER NOT NULL,
            name                     VARCHAR NOT NULL,
            cost                     DOUBLE PRECISION,
            market_group_id          BIGINT REFERENCES market_groups(id),
            blueprint_id             BIGINT REFERENCES blueprints(id),
            volume                   DOUBLE PRECISION,
            production_level         INTEGER,
            base_item                BOOLEAN NOT NULL DEFAULT FALSE,
            cpp_market_adjusted_price DOUBLE PRECISION,
            cpp_market_average_price  DOUBLE PRECISION,
            description              TEXT,
            market_group_path        TEXT NOT NULL DEFAULT '[]',
            mass                     DOUBLE PRECISION,
            packaged_volume          DOUBLE PRECISION,
            weekly_avg_price         DOUBLE PRECISION,
            faction                  BOOLEAN NOT NULL DEFAULT FALSE,
            slug                     VARCHAR UNIQUE,
            created_at               TIMESTAMP,
            updated_at               TIMESTAMP
        )
    """)
    op.execute("ALTER TABLE universe_types DROP COLUMN IF EXISTS cost")
    op.execute("ALTER TABLE universe_types DROP COLUMN IF EXISTS weekly_avg_price")
    op.execute("ALTER TABLE universe_types DROP COLUMN IF EXISTS base_item")
