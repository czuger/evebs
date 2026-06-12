"""dual window forecast mvs 7d and 30d

Revision ID: 1ecb2458e196
Revises: a60d985048e5
Create Date: 2026-06-12 16:57:10.505345

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1ecb2458e196'
down_revision: Union[str, None] = 'a60d985048e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Two training windows per item over Jita sales_finals: last 7 days and last 30 days, each
# forecasting the next 7 days. `y` is the regression target — volume-weighted daily price for
# the price MV, daily total volume for the volume MV. Per-window slope/intercept/r2/n +
# confidence; `spread`/`spread_percent` compare the 30-day vs 7-day forecast per date.
def _mv_sql(name, y_expr):
    return f"""
CREATE MATERIALIZED VIEW {name} AS
WITH daily AS (
    SELECT eve_item_id AS type_id, day,
           EXTRACT(EPOCH FROM day) / 86400.0 AS x,
           {y_expr} AS y
    FROM sales_finals
    WHERE universe_system_id = 30000142 AND day >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY eve_item_id, day
),
reg AS (
    SELECT type_id,
        regr_slope(y, x)     FILTER (WHERE day >= CURRENT_DATE - INTERVAL '7 days') AS slope_7d,
        regr_intercept(y, x) FILTER (WHERE day >= CURRENT_DATE - INTERVAL '7 days') AS intercept_7d,
        regr_r2(y, x)        FILTER (WHERE day >= CURRENT_DATE - INTERVAL '7 days') AS r2_7d,
        regr_count(y, x)     FILTER (WHERE day >= CURRENT_DATE - INTERVAL '7 days') AS n_7d,
        regr_slope(y, x)     AS slope_30d,
        regr_intercept(y, x) AS intercept_30d,
        regr_r2(y, x)        AS r2_30d,
        regr_count(y, x)     AS n_30d
    FROM daily
    GROUP BY type_id
    HAVING regr_count(y, x) >= 2
),
pred AS (
    SELECT
        r.type_id,
        (CURRENT_DATE + d)::date AS forecast_date,
        CASE WHEN r.slope_7d IS NOT NULL
             THEN GREATEST(r.intercept_7d + r.slope_7d * (EXTRACT(EPOCH FROM (CURRENT_DATE + d)) / 86400.0), 0)
        END AS forecast_7d,
        CASE WHEN r.slope_30d IS NOT NULL
             THEN GREATEST(r.intercept_30d + r.slope_30d * (EXTRACT(EPOCH FROM (CURRENT_DATE + d)) / 86400.0), 0)
        END AS forecast_30d,
        r.slope_7d, r.intercept_7d, r.r2_7d, r.n_7d,
        r.slope_30d, r.intercept_30d, r.r2_30d, r.n_30d
    FROM reg r
    CROSS JOIN generate_series(1, 7) AS d
)
SELECT
    type_id, forecast_date, forecast_7d, forecast_30d,
    ABS(forecast_30d - forecast_7d)                            AS spread,
    ABS((forecast_30d - forecast_7d) / NULLIF(forecast_30d, 0)) AS spread_percent,
    slope_7d, intercept_7d, r2_7d, n_7d,
    slope_30d, intercept_30d, r2_30d, n_30d,
    CASE WHEN r2_7d >= 0.85 AND n_7d >= 5 THEN 'high'
         WHEN r2_7d >= 0.60 AND n_7d >= 3 THEN 'medium'
         ELSE 'low' END AS confidence_7d,
    CASE WHEN r2_30d >= 0.85 AND n_30d >= 20 THEN 'high'
         WHEN r2_30d >= 0.60 AND n_30d >= 10 THEN 'medium'
         ELSE 'low' END AS confidence_30d
FROM pred
WITH NO DATA
"""


def _create_mv(conn, name, y_expr, ix):
    conn.execute(sa.text(_mv_sql(name, y_expr)))
    conn.execute(sa.text(f'CREATE INDEX {ix} ON {name} (type_id)'))
    conn.execute(sa.text(f'REFRESH MATERIALIZED VIEW {name}'))


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text('DROP MATERIALIZED VIEW IF EXISTS jita_price_forecast_linear_regression'))
    conn.execute(sa.text('DROP MATERIALIZED VIEW IF EXISTS jita_volume_forecast_linear_regression'))
    _create_mv(conn, 'jita_price_forecast_linear_regression',
               'SUM(volume * price) / NULLIF(SUM(volume), 0)', 'ix_jpflr_type_id')
    _create_mv(conn, 'jita_volume_forecast_linear_regression',
               'SUM(volume)::float', 'ix_jvflr_type_id')


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
