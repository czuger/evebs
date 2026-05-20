"""Add p5/p20/p80/p95 percentile columns to market_seller_prices and market_buyer_prices.

Revision ID: 0021_market_percentiles
Revises: 0020_replace_trade_hubs
Create Date: 2026-05-20

"""
from alembic import op

revision = '0021_market_percentiles'
down_revision = '0020_replace_trade_hubs'
branch_labels = None
depends_on = None


_SELLER_SQL = """
    CREATE MATERIALIZED VIEW market_seller_prices AS
    WITH ranked AS (
        SELECT system_id, type_id, price, volume_remain,
            SUM(volume_remain) OVER (
                PARTITION BY system_id, type_id
                ORDER BY price ASC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS cum_vol,
            SUM(volume_remain) OVER (
                PARTITION BY system_id, type_id
            ) AS total_vol
        FROM market_orders
        WHERE is_buy_order = FALSE
    )
    SELECT system_id, type_id,
        MIN(price) FILTER (WHERE cum_vol >= total_vol * 0.05)  AS p5_price,
        MIN(price) FILTER (WHERE cum_vol >= total_vol * 0.10)  AS p10_price,
        MIN(price) FILTER (WHERE cum_vol >= total_vol * 0.20)  AS p20_price,
        MIN(price) FILTER (WHERE cum_vol >= total_vol * 0.80)  AS p80_price,
        MIN(price) FILTER (WHERE cum_vol >= total_vol * 0.90)  AS p90_price,
        MIN(price) FILTER (WHERE cum_vol >= total_vol * 0.95)  AS p95_price,
        MAX(total_vol)                                          AS volume
    FROM ranked
    GROUP BY system_id, type_id
"""

_BUYER_SQL = """
    CREATE MATERIALIZED VIEW market_buyer_prices AS
    WITH ranked AS (
        SELECT system_id, type_id, price, volume_remain,
            SUM(volume_remain) OVER (
                PARTITION BY system_id, type_id
                ORDER BY price DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS cum_vol,
            SUM(volume_remain) OVER (
                PARTITION BY system_id, type_id
            ) AS total_vol
        FROM market_orders
        WHERE is_buy_order = TRUE
    )
    SELECT system_id, type_id,
        MAX(price) FILTER (WHERE cum_vol >= total_vol * 0.05)  AS p95_price,
        MAX(price) FILTER (WHERE cum_vol >= total_vol * 0.10)  AS p90_price,
        MAX(price) FILTER (WHERE cum_vol >= total_vol * 0.20)  AS p80_price,
        MAX(price) FILTER (WHERE cum_vol >= total_vol * 0.80)  AS p20_price,
        MAX(price) FILTER (WHERE cum_vol >= total_vol * 0.90)  AS p10_price,
        MAX(price) FILTER (WHERE cum_vol >= total_vol * 0.95)  AS p5_price,
        MAX(total_vol)                                          AS volume
    FROM ranked
    GROUP BY system_id, type_id
"""


def upgrade():
    op.execute("DROP MATERIALIZED VIEW IF EXISTS market_seller_prices CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS market_buyer_prices CASCADE")

    op.execute(_SELLER_SQL)
    op.execute("""
        CREATE UNIQUE INDEX idx_market_seller_prices_system_type
        ON market_seller_prices (system_id, type_id)
    """)

    op.execute(_BUYER_SQL)
    op.execute("""
        CREATE UNIQUE INDEX idx_market_buyer_prices_system_type
        ON market_buyer_prices (system_id, type_id)
    """)


def downgrade():
    op.execute("DROP MATERIALIZED VIEW IF EXISTS market_seller_prices CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS market_buyer_prices CASCADE")

    op.execute("""
        CREATE MATERIALIZED VIEW market_seller_prices AS
        WITH ranked AS (
            SELECT system_id, type_id, price, volume_remain,
                SUM(volume_remain) OVER (
                    PARTITION BY system_id, type_id
                    ORDER BY price ASC
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS cum_vol,
                SUM(volume_remain) OVER (
                    PARTITION BY system_id, type_id
                ) AS total_vol
            FROM market_orders
            WHERE is_buy_order = FALSE
        )
        SELECT system_id, type_id,
            MIN(price) FILTER (WHERE cum_vol >= total_vol * 0.05) AS p10_price,
            MAX(total_vol)                                         AS volume
        FROM ranked
        GROUP BY system_id, type_id
    """)
    op.execute("""
        CREATE UNIQUE INDEX idx_market_seller_prices_system_type
        ON market_seller_prices (system_id, type_id)
    """)

    op.execute("""
        CREATE MATERIALIZED VIEW market_buyer_prices AS
        WITH ranked AS (
            SELECT system_id, type_id, price, volume_remain,
                SUM(volume_remain) OVER (
                    PARTITION BY system_id, type_id
                    ORDER BY price DESC
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS cum_vol,
                SUM(volume_remain) OVER (
                    PARTITION BY system_id, type_id
                ) AS total_vol
            FROM market_orders
            WHERE is_buy_order = TRUE
        )
        SELECT system_id, type_id,
            MAX(price) FILTER (WHERE cum_vol >= total_vol * 0.10) AS p90_price,
            MAX(total_vol)                                         AS volume
        FROM ranked
        GROUP BY system_id, type_id
    """)
    op.execute("""
        CREATE UNIQUE INDEX idx_market_buyer_prices_system_type
        ON market_buyer_prices (system_id, type_id)
    """)
