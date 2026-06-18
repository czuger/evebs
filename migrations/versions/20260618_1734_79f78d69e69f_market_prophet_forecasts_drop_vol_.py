"""market_prophet_forecasts drop vol spreads 3col index price_direction

Revision ID: 79f78d69e69f
Revises: 13cf4362e8a8
Create Date: 2026-06-18 17:34:11.725192

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '79f78d69e69f'
down_revision: Union[str, None] = '13cf4362e8a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('market_prophet_forecasts', 'vol_spread')
    op.drop_column('market_prophet_forecasts', 'vol_spread_pct')
    op.drop_constraint('uq_market_prophet_forecasts_region_type_conf_date',
                       'market_prophet_forecasts', type_='unique')
    op.create_unique_constraint('uq_market_prophet_forecasts_region_type_date',
                                'market_prophet_forecasts',
                                ['region_id', 'type_id', 'forecast_date'])
    op.add_column('market_prophet_forecasts',
                  sa.Column('price_direction', sa.SmallInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column('market_prophet_forecasts', 'price_direction')
    op.drop_constraint('uq_market_prophet_forecasts_region_type_date',
                       'market_prophet_forecasts', type_='unique')
    op.create_unique_constraint('uq_market_prophet_forecasts_region_type_conf_date',
                                'market_prophet_forecasts',
                                ['region_id', 'type_id', 'confidence', 'forecast_date'])
    op.add_column('market_prophet_forecasts',
                  sa.Column('vol_spread_pct', sa.Float(), nullable=False, server_default='0'))
    op.add_column('market_prophet_forecasts',
                  sa.Column('vol_spread', sa.Float(), nullable=False, server_default='0'))
