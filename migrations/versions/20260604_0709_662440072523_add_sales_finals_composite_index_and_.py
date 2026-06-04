"""add sales_finals composite index and jita_market_analytics table

Revision ID: 662440072523
Revises: ed2f10479334
Create Date: 2026-06-04 07:09:38.564953

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '662440072523'
down_revision: Union[str, None] = 'ed2f10479334'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    conn.execute(sa.text("""
        CREATE INDEX ix_sales_finals_system_item_updated
            ON sales_finals (universe_system_id, eve_item_id, updated_at)
    """))

    conn.execute(sa.text("""
        CREATE TABLE jita_market_analytics (
            id                BIGINT PRIMARY KEY,
            min_sell_price    FLOAT,
            price_forecast_3d FLOAT,
            updated_at        TIMESTAMP
        )
    """))


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
