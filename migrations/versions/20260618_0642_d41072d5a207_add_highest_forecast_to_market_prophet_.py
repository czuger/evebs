"""add highest forecast to market_prophet_forecasts

Revision ID: d41072d5a207
Revises: f6e95b889029
Create Date: 2026-06-18 06:42:40.748922

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd41072d5a207'
down_revision: Union[str, None] = 'f6e95b889029'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('market_prophet_forecasts', sa.Column('high_predicted', sa.Float(), nullable=True))
    op.add_column('market_prophet_forecasts', sa.Column('high_lower', sa.Float(), nullable=True))
    op.add_column('market_prophet_forecasts', sa.Column('high_upper', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('market_prophet_forecasts', 'high_upper')
    op.drop_column('market_prophet_forecasts', 'high_lower')
    op.drop_column('market_prophet_forecasts', 'high_predicted')
