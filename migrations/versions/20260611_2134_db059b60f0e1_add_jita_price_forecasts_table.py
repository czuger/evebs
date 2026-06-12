"""add jita_price_forecasts table

Revision ID: db059b60f0e1
Revises: 1f88bdd6f3f0
Create Date: 2026-06-11 21:34:48.470812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'db059b60f0e1'
down_revision: Union[str, None] = '1f88bdd6f3f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'jita_price_forecasts',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column('price_forecast_3d', sa.Float(), nullable=True),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('jita_price_forecasts')
