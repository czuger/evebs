"""Add jita_prices materialized view

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-05-29

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, None] = 'f6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CREATE_MV = """
CREATE MATERIALIZED VIEW jita_prices AS
WITH
jita AS (
    SELECT id FROM trade_hubs WHERE eve_system_id = 30000142
),
sell AS (
    SELECT ei.cpp_eve_item_id, pto.price, pto.volume_remain,
        SUM(pto.volume_remain) OVER (
            PARTITION BY pto.eve_item_id ORDER BY pto.price ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cum_vol,
        SUM(pto.volume_remain) OVER (PARTITION BY pto.eve_item_id) AS total_vol
    FROM public_trade_orders pto
    JOIN eve_items ei ON pto.eve_item_id = ei.id
    WHERE pto.is_buy_order = false AND pto.trade_hub_id = (SELECT id FROM jita)
),
sell_p10 AS (
    SELECT cpp_eve_item_id, MIN(price) AS min_sell_price
    FROM sell WHERE cum_vol >= total_vol * 0.10
    GROUP BY cpp_eve_item_id
),
buy AS (
    SELECT ei.cpp_eve_item_id, pto.price, pto.volume_remain,
        SUM(pto.volume_remain) OVER (
            PARTITION BY pto.eve_item_id ORDER BY pto.price ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cum_vol,
        SUM(pto.volume_remain) OVER (PARTITION BY pto.eve_item_id) AS total_vol
    FROM public_trade_orders pto
    JOIN eve_items ei ON pto.eve_item_id = ei.id
    WHERE pto.is_buy_order = true AND pto.trade_hub_id = (SELECT id FROM jita)
),
buy_p90 AS (
    SELECT cpp_eve_item_id, MIN(price) * 0.9 AS max_buy_price
    FROM buy WHERE cum_vol >= total_vol * 0.90
    GROUP BY cpp_eve_item_id
),
all_items AS (
    SELECT cpp_eve_item_id FROM sell_p10
    UNION
    SELECT cpp_eve_item_id FROM buy_p90
)
SELECT a.cpp_eve_item_id, s.min_sell_price, b.max_buy_price,
    s.min_sell_price - b.max_buy_price AS spread
FROM all_items a
LEFT JOIN sell_p10 s ON a.cpp_eve_item_id = s.cpp_eve_item_id
LEFT JOIN buy_p90  b ON a.cpp_eve_item_id = b.cpp_eve_item_id
WITH NO DATA
"""


def upgrade() -> None:
    op.execute(CREATE_MV)
    op.execute('CREATE UNIQUE INDEX ON jita_prices (cpp_eve_item_id)')


def downgrade() -> None:
    op.execute('DROP MATERIALIZED VIEW IF EXISTS jita_prices')
