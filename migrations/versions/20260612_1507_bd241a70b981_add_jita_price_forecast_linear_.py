"""add jita_price_forecast_linear_regression materialized view

Revision ID: bd241a70b981
Revises: 8f77fa1ce9d9
Create Date: 2026-06-12 15:07:04.222719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'bd241a70b981'
down_revision: Union[str, None] = '8f77fa1ce9d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_MV_SQL = """
CREATE MATERIALIZED VIEW jita_price_forecast_linear_regression AS
WITH hist AS (
    SELECT type_id, date, average, EXTRACT(EPOCH FROM date) / 86400.0 AS x
    FROM market_histories
    WHERE region_id = 10000002 AND average IS NOT NULL
      AND date >= CURRENT_DATE - INTERVAL '30 days'
),
reg AS (
    SELECT type_id,
        regr_slope(average, x)     FILTER (WHERE date >= CURRENT_DATE - INTERVAL '7 days') AS slope_7d,
        regr_intercept(average, x) FILTER (WHERE date >= CURRENT_DATE - INTERVAL '7 days') AS intercept_7d,
        regr_r2(average, x)        FILTER (WHERE date >= CURRENT_DATE - INTERVAL '7 days') AS r2_7d,
        regr_count(average, x)     FILTER (WHERE date >= CURRENT_DATE - INTERVAL '7 days') AS n_7d,
        regr_slope(average, x)     AS slope_30d,
        regr_intercept(average, x) AS intercept_30d,
        regr_r2(average, x)        AS r2_30d,
        regr_count(average, x)     AS n_30d
    FROM hist
    GROUP BY type_id
    HAVING regr_count(average, x) >= 2
)
SELECT
    r.type_id,
    (CURRENT_DATE + d)::date AS forecast_date,
    CASE WHEN d <= 7 AND r.slope_7d IS NOT NULL
         THEN r.intercept_7d + r.slope_7d * (EXTRACT(EPOCH FROM (CURRENT_DATE + d)) / 86400.0)
    END AS forecast_7d,
    CASE WHEN r.slope_30d IS NOT NULL
         THEN r.intercept_30d + r.slope_30d * (EXTRACT(EPOCH FROM (CURRENT_DATE + d)) / 86400.0)
    END AS forecast_30d,
    r.r2_7d, r.r2_30d, r.n_7d, r.n_30d,
    CASE WHEN r.r2_7d >= 0.85 AND r.n_7d >= 5 THEN 'high'
         WHEN r.r2_7d >= 0.60 AND r.n_7d >= 3 THEN 'medium'
         ELSE 'low' END AS confidence_7d,
    CASE WHEN r.r2_30d >= 0.85 AND r.n_30d >= 20 THEN 'high'
         WHEN r.r2_30d >= 0.60 AND r.n_30d >= 10 THEN 'medium'
         ELSE 'low' END AS confidence_30d
FROM reg r
CROSS JOIN generate_series(1, 30) AS d
WITH NO DATA
"""


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(_MV_SQL))
    conn.execute(sa.text('CREATE INDEX ix_jpflr_type_id ON jita_price_forecast_linear_regression (type_id)'))
    conn.execute(sa.text('REFRESH MATERIALIZED VIEW jita_price_forecast_linear_regression'))


def downgrade() -> None:
    op.execute(sa.text('DROP MATERIALIZED VIEW IF EXISTS jita_price_forecast_linear_regression'))
