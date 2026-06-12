"""rework forecast MVs on sales_finals and add volume forecast

Revision ID: a60d985048e5
Revises: bd241a70b981
Create Date: 2026-06-12 16:20:50.482222

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a60d985048e5'
down_revision: Union[str, None] = 'bd241a70b981'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# `y` is the regression target: volume-weighted daily price for the price MV, daily total
# volume for the volume MV. Single 7-day training window; forecast_3d is NULL past day 3.
def _mv_sql(name, y_expr):
    return f"""
CREATE MATERIALIZED VIEW {name} AS
WITH daily AS (
    SELECT eve_item_id AS type_id, day,
           EXTRACT(EPOCH FROM day) / 86400.0 AS x,
           {y_expr} AS y
    FROM sales_finals
    WHERE universe_system_id = 30000142 AND day >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY eve_item_id, day
),
reg AS (
    SELECT type_id,
           regr_slope(y, x)     AS slope,
           regr_intercept(y, x) AS intercept,
           regr_r2(y, x)        AS r2,
           regr_count(y, x)     AS n
    FROM daily
    GROUP BY type_id
    HAVING regr_count(y, x) >= 2
)
SELECT
    r.type_id,
    (CURRENT_DATE + d)::date AS forecast_date,
    CASE WHEN d <= 3 AND r.slope IS NOT NULL
         THEN GREATEST(r.intercept + r.slope * (EXTRACT(EPOCH FROM (CURRENT_DATE + d)) / 86400.0), 0)
    END AS forecast_3d,
    CASE WHEN r.slope IS NOT NULL
         THEN GREATEST(r.intercept + r.slope * (EXTRACT(EPOCH FROM (CURRENT_DATE + d)) / 86400.0), 0)
    END AS forecast_7d,
    r.slope, r.intercept, r.r2, r.n,
    CASE WHEN r.r2 >= 0.85 AND r.n >= 5 THEN 'high'
         WHEN r.r2 >= 0.60 AND r.n >= 3 THEN 'medium'
         ELSE 'low' END AS confidence
FROM reg r
CROSS JOIN generate_series(1, 7) AS d
WITH NO DATA
"""


def _create_mv(conn, name, y_expr, ix):
    conn.execute(sa.text(_mv_sql(name, y_expr)))
    conn.execute(sa.text(f'CREATE INDEX {ix} ON {name} (type_id)'))
    conn.execute(sa.text(f'REFRESH MATERIALIZED VIEW {name}'))


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text('DROP INDEX IF EXISTS ix_sales_finals_system_item_updated'))
    conn.execute(sa.text('CREATE INDEX ix_sales_finals_system_item_day '
                         'ON sales_finals (universe_system_id, eve_item_id, day)'))

    conn.execute(sa.text('DROP MATERIALIZED VIEW IF EXISTS jita_price_forecast_linear_regression'))
    _create_mv(conn, 'jita_price_forecast_linear_regression',
               'SUM(volume * price) / NULLIF(SUM(volume), 0)', 'ix_jpflr_type_id')
    _create_mv(conn, 'jita_volume_forecast_linear_regression',
               'SUM(volume)::float', 'ix_jvflr_type_id')


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
