"""create market_prophet_forecasts table

Revision ID: f6e95b889029
Revises: 02c1fbcf1862
Create Date: 2026-06-17 22:48:19.896738

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f6e95b889029'
down_revision: Union[str, None] = '02c1fbcf1862'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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
        sa.Column('vol_predicted', sa.Float(), nullable=True),
        sa.Column('vol_lower', sa.Float(), nullable=True),
        sa.Column('vol_upper', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('region_id', 'type_id', 'forecast_date',
                            name='uq_market_prophet_forecasts_region_type_date'),
    )


def downgrade() -> None:
    op.drop_table('market_prophet_forecasts')
