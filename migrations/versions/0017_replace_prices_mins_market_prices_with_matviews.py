"""replace prices_mins and market_prices tables with materialized views

Revision ID: 0017_market_price_matviews
Revises: 0016_industry_interesting_items
Create Date: 2026-05-20

"""
from alembic import op

revision = '0017_market_price_matviews'
down_revision = '0016_industry_interesting_items'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP TABLE IF EXISTS prices_mins")
    op.execute("DROP TABLE IF EXISTS market_prices")

    op.execute("""
        CREATE INDEX idx_market_orders_sell
        ON market_orders (system_id, type_id, price)
        WHERE is_buy_order = FALSE
    """)
    op.execute("""
        CREATE INDEX idx_market_orders_buy
        ON market_orders (system_id, type_id, price)
        WHERE is_buy_order = TRUE
    """)

    op.execute("""
        CREATE MATERIALIZED VIEW market_seller_prices AS
        SELECT
            type_id,
            system_id,
            PERCENTILE_CONT(0.10) WITHIN GROUP (ORDER BY price)        AS p10_price,
            SUM(volume_remain)                                          AS volume
        FROM market_orders
        WHERE is_buy_order = FALSE
        GROUP BY system_id, type_id
    """)
    op.execute("""
        CREATE UNIQUE INDEX idx_market_seller_prices_system_type
        ON market_seller_prices (system_id, type_id)
    """)

    op.execute("""
        CREATE MATERIALIZED VIEW market_buyer_prices AS
        SELECT
            type_id,
            system_id,
            PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY price)        AS p90_price,
            SUM(volume_remain)                                          AS volume
        FROM market_orders
        WHERE is_buy_order = TRUE
        GROUP BY system_id, type_id
    """)
    op.execute("""
        CREATE UNIQUE INDEX idx_market_buyer_prices_system_type
        ON market_buyer_prices (system_id, type_id)
    """)


def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_market_orders_sell")
    op.execute("DROP INDEX IF EXISTS idx_market_orders_buy")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS market_seller_prices CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS market_buyer_prices CASCADE")

    op.execute("""
        CREATE TABLE prices_mins (
            id          SERIAL PRIMARY KEY,
            eve_item_id INTEGER REFERENCES universe_types(id),
            trade_hub_id INTEGER REFERENCES trade_hubs(id),
            min_price   DOUBLE PRECISION,
            volume      BIGINT,
            created_at  TIMESTAMP,
            updated_at  TIMESTAMP,
            UNIQUE (trade_hub_id, eve_item_id)
        )
    """)
    op.execute("""
        CREATE TABLE market_prices (
            id          BIGSERIAL PRIMARY KEY,
            type_id     BIGINT NOT NULL REFERENCES universe_types(id),
            adjusted_price DOUBLE PRECISION,
            average_price  DOUBLE PRECISION
        )
    """)
    op.execute("""
        CREATE UNIQUE INDEX ix_market_prices_type_id ON market_prices (type_id)
    """)
