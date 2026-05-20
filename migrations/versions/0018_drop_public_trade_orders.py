"""drop public_trade_orders table

Revision ID: 0018_drop_public_trade_orders
Revises: 0017_market_price_matviews
Create Date: 2026-05-20

"""
from alembic import op

revision = '0018_drop_public_trade_orders'
down_revision = '0017_market_price_matviews'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('public_trade_orders')


def downgrade():
    op.execute("""
        CREATE TABLE public_trade_orders (
            id              BIGSERIAL PRIMARY KEY,
            trade_hub_id    BIGINT NOT NULL REFERENCES trade_hubs(id),
            eve_item_id     BIGINT NOT NULL REFERENCES universe_types(id),
            order_id        BIGINT NOT NULL UNIQUE,
            is_buy_order    BOOLEAN NOT NULL,
            end_time        TIMESTAMP NOT NULL,
            price           DOUBLE PRECISION NOT NULL,
            range           VARCHAR NOT NULL,
            volume_remain   BIGINT NOT NULL,
            volume_total    BIGINT NOT NULL,
            min_volume      BIGINT NOT NULL,
            touched         BOOLEAN NOT NULL DEFAULT FALSE,
            created_at      TIMESTAMP,
            updated_at      TIMESTAMP
        )
    """)
