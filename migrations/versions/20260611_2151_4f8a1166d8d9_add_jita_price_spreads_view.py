"""add jita_price_spreads view

Revision ID: 4f8a1166d8d9
Revises: db059b60f0e1
Create Date: 2026-06-11 21:51:10.256826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4f8a1166d8d9'
down_revision: Union[str, None] = 'db059b60f0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_VIEW_SQL = """
CREATE VIEW jita_price_spreads AS
SELECT
    f.id                                     AS id,
    ei.name                                  AS item_name,
    ei.slug                                  AS item_slug,
    m.min_sell_price                         AS min_sell_price,
    f.price_forecast_3d                      AS price_forecast_3d,
    f.method                                 AS method,
    (f.price_forecast_3d - m.min_sell_price) AS spread,
    CASE WHEN m.min_sell_price > 0
         THEN (f.price_forecast_3d - m.min_sell_price) / m.min_sell_price END AS spread_pcent,
    CASE
        WHEN f.method = 'min_price' OR m.min_sell_price <= 0 THEN 'flat'
        WHEN (f.price_forecast_3d - m.min_sell_price) / m.min_sell_price >=  0.02 THEN 'up'
        WHEN (f.price_forecast_3d - m.min_sell_price) / m.min_sell_price <= -0.02 THEN 'down'
        ELSE 'flat'
    END                                      AS direction,
    CASE
        WHEN f.method = 'min_price' OR m.min_sell_price <= 0 THEN FALSE
        ELSE ABS((f.price_forecast_3d - m.min_sell_price) / m.min_sell_price) >= 0.10
    END                                      AS is_hard
FROM jita_price_forecasts f
JOIN jita_min_prices m ON m.id = f.id
JOIN eve_items ei     ON ei.id = f.id
"""


def upgrade() -> None:
    op.execute(sa.text("DROP VIEW IF EXISTS jita_price_spreads"))
    op.execute(sa.text(_VIEW_SQL))


def downgrade() -> None:
    op.execute(sa.text("DROP VIEW IF EXISTS jita_price_spreads"))
