"""rebuild market_prophet_forecasts no-nulls spreads errors

Revision ID: 13cf4362e8a8
Revises: d41072d5a207
Create Date: 2026-06-18 11:30:25.381902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '13cf4362e8a8'
down_revision: Union[str, None] = 'd41072d5a207'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _price_vol_cols():
    return [
        sa.Column('avg_predicted', sa.Float(), nullable=False),
        sa.Column('avg_lower', sa.Float(), nullable=False),
        sa.Column('avg_upper', sa.Float(), nullable=False),
        sa.Column('low_predicted', sa.Float(), nullable=False),
        sa.Column('low_lower', sa.Float(), nullable=False),
        sa.Column('low_upper', sa.Float(), nullable=False),
        sa.Column('high_predicted', sa.Float(), nullable=False),
        sa.Column('high_lower', sa.Float(), nullable=False),
        sa.Column('high_upper', sa.Float(), nullable=False),
        sa.Column('vol_predicted', sa.Float(), nullable=False),
        sa.Column('vol_lower', sa.Float(), nullable=False),
        sa.Column('vol_upper', sa.Float(), nullable=False),
    ]


def upgrade() -> None:
    # Existing forecast data is disposable (recomputed) — drop and recreate.
    op.drop_table('market_prophet_forecasts')
    op.create_table(
        'market_prophet_forecasts',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('type_id', sa.BigInteger(), nullable=False),
        sa.Column('forecast_date', sa.Date(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        *_price_vol_cols(),
        sa.Column('price_spread', sa.Float(), nullable=False),
        sa.Column('price_spread_pct', sa.Float(), nullable=False),
        sa.Column('vol_spread', sa.Float(), nullable=False),
        sa.Column('vol_spread_pct', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('region_id', 'type_id', 'confidence', 'forecast_date',
                            name='uq_market_prophet_forecasts_region_type_conf_date'),
    )
    op.create_table(
        'market_prophet_forecast_errors',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('type_id', sa.BigInteger(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('region_id', 'type_id', 'confidence',
                            name='uq_market_prophet_forecast_errors_region_type_conf'),
    )


def downgrade() -> None:
    op.drop_table('market_prophet_forecast_errors')
    op.drop_table('market_prophet_forecasts')
    # Recreate the prior (nullable-vol, status) schema (best-effort; data is disposable).
    op.create_table(
        'market_prophet_forecasts',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('type_id', sa.BigInteger(), nullable=False),
        sa.Column('forecast_date', sa.Date(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('avg_predicted', sa.Float(), nullable=True),
        sa.Column('avg_lower', sa.Float(), nullable=True),
        sa.Column('avg_upper', sa.Float(), nullable=True),
        sa.Column('low_predicted', sa.Float(), nullable=True),
        sa.Column('low_lower', sa.Float(), nullable=True),
        sa.Column('low_upper', sa.Float(), nullable=True),
        sa.Column('high_predicted', sa.Float(), nullable=True),
        sa.Column('high_lower', sa.Float(), nullable=True),
        sa.Column('high_upper', sa.Float(), nullable=True),
        sa.Column('vol_predicted', sa.Float(), nullable=True),
        sa.Column('vol_lower', sa.Float(), nullable=True),
        sa.Column('vol_upper', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('region_id', 'type_id', 'forecast_date',
                            name='uq_market_prophet_forecasts_region_type_date'),
    )
