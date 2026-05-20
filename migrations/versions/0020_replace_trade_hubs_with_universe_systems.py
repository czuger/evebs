"""Replace trade_hubs table with universe_systems; rename trade_hub_id -> system_id everywhere.

Revision ID: 0020_replace_trade_hubs
Revises: 0019_replace_eve_items
Create Date: 2026-05-20

"""
from alembic import op

revision = '0020_replace_trade_hubs'
down_revision = '0019_replace_eve_items'
branch_labels = None
depends_on = None


def upgrade():
    tables = [
        'buy_orders_analytics',
        'prices_advices',
        'production_lists',
        'user_sale_orders',
        'sales_finals',
        'weekly_price_details',
    ]

    # 1. Add system_id to each dependent table and populate from trade_hubs
    for tbl in tables:
        op.execute(f"ALTER TABLE {tbl} ADD COLUMN system_id BIGINT")
        op.execute(f"""
            UPDATE {tbl} t
            SET system_id = th.eve_system_id
            FROM trade_hubs th
            WHERE th.id = t.trade_hub_id
        """)

    # 2. Drop unique constraints and FKs that reference trade_hub_id, then drop the column
    op.execute("ALTER TABLE buy_orders_analytics DROP CONSTRAINT IF EXISTS buy_orders_analytics_trade_hub_id_eve_item_id_key")
    op.execute("ALTER TABLE prices_advices DROP CONSTRAINT IF EXISTS prices_advices_eve_item_id_trade_hub_id_key")
    op.execute("ALTER TABLE weekly_price_details DROP CONSTRAINT IF EXISTS weekly_price_details_eve_item_id_trade_hub_id_day_key")

    for tbl in tables:
        # drop FK constraint (names vary, so iterate candidate names)
        op.execute(f"""
            DO $$
            DECLARE r RECORD;
            BEGIN
                FOR r IN
                    SELECT conname FROM pg_constraint
                    WHERE conrelid = '{tbl}'::regclass AND contype = 'f'
                      AND conname LIKE '%trade_hub%'
                LOOP
                    EXECUTE 'ALTER TABLE {tbl} DROP CONSTRAINT ' || quote_ident(r.conname);
                END LOOP;
            END $$;
        """)
        op.execute(f"ALTER TABLE {tbl} DROP COLUMN trade_hub_id")

    # 3. Set NOT NULL and add new FK constraints
    for tbl in tables:
        op.execute(f"ALTER TABLE {tbl} ALTER COLUMN system_id SET NOT NULL")
        op.execute(f"""
            ALTER TABLE {tbl}
            ADD CONSTRAINT {tbl}_system_id_fkey
            FOREIGN KEY (system_id) REFERENCES universe_systems(id)
        """)

    # 4. Recreate unique constraints with the new column name
    op.execute("ALTER TABLE buy_orders_analytics ADD CONSTRAINT buy_orders_analytics_system_id_eve_item_id_key UNIQUE (system_id, eve_item_id)")
    op.execute("ALTER TABLE prices_advices ADD CONSTRAINT prices_advices_eve_item_id_system_id_key UNIQUE (eve_item_id, system_id)")
    op.execute("ALTER TABLE weekly_price_details ADD CONSTRAINT weekly_price_details_eve_item_id_system_id_day_key UNIQUE (eve_item_id, system_id, day)")

    # 5. Create universe_systems_users association table
    op.execute("""
        CREATE TABLE universe_systems_users (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            universe_system_id BIGINT REFERENCES universe_systems(id)
        )
    """)
    op.execute("""
        INSERT INTO universe_systems_users (user_id, universe_system_id)
        SELECT thu.user_id, th.eve_system_id
        FROM trade_hubs_users thu
        JOIN trade_hubs th ON th.id = thu.trade_hub_id
    """)

    # 6. Drop old association table and trade_hubs itself
    op.execute("DROP TABLE trade_hubs_users")
    op.execute("DROP TABLE trade_hubs")


def downgrade():
    op.execute("""
        CREATE TABLE trade_hubs (
            id SERIAL PRIMARY KEY,
            eve_system_id INTEGER NOT NULL UNIQUE,
            name VARCHAR NOT NULL,
            region_id BIGINT REFERENCES universe_regions(id),
            inner BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    op.execute("""
        INSERT INTO trade_hubs (eve_system_id, name)
        SELECT DISTINCT us.id, us.name
        FROM universe_systems us
        JOIN universe_systems_users usu ON usu.universe_system_id = us.id
    """)
    op.execute("""
        CREATE TABLE trade_hubs_users (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            trade_hub_id INTEGER REFERENCES trade_hubs(id)
        )
    """)
    op.execute("""
        INSERT INTO trade_hubs_users (user_id, trade_hub_id)
        SELECT usu.user_id, th.id
        FROM universe_systems_users usu
        JOIN trade_hubs th ON th.eve_system_id = usu.universe_system_id
    """)
    op.execute("DROP TABLE universe_systems_users")

    tables = [
        'buy_orders_analytics',
        'prices_advices',
        'production_lists',
        'user_sale_orders',
        'sales_finals',
        'weekly_price_details',
    ]

    op.execute("ALTER TABLE buy_orders_analytics DROP CONSTRAINT IF EXISTS buy_orders_analytics_system_id_eve_item_id_key")
    op.execute("ALTER TABLE prices_advices DROP CONSTRAINT IF EXISTS prices_advices_eve_item_id_system_id_key")
    op.execute("ALTER TABLE weekly_price_details DROP CONSTRAINT IF EXISTS weekly_price_details_eve_item_id_system_id_day_key")

    for tbl in tables:
        op.execute(f"ALTER TABLE {tbl} DROP CONSTRAINT IF EXISTS {tbl}_system_id_fkey")
        op.execute(f"ALTER TABLE {tbl} ADD COLUMN trade_hub_id INTEGER")
        op.execute(f"""
            UPDATE {tbl} t
            SET trade_hub_id = th.id
            FROM trade_hubs th
            WHERE th.eve_system_id = t.system_id
        """)
        op.execute(f"ALTER TABLE {tbl} DROP COLUMN system_id")

    op.execute("ALTER TABLE buy_orders_analytics ADD CONSTRAINT buy_orders_analytics_trade_hub_id_eve_item_id_key UNIQUE (trade_hub_id, eve_item_id)")
    op.execute("ALTER TABLE prices_advices ADD CONSTRAINT prices_advices_eve_item_id_trade_hub_id_key UNIQUE (eve_item_id, trade_hub_id)")
    op.execute("ALTER TABLE weekly_price_details ADD CONSTRAINT weekly_price_details_eve_item_id_trade_hub_id_day_key UNIQUE (eve_item_id, trade_hub_id, day)")
