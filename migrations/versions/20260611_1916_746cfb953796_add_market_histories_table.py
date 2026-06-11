"""add market_histories table

Revision ID: 746cfb953796
Revises: 01f93a40df71
Create Date: 2026-06-11 19:16:28.611038

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '746cfb953796'
down_revision: Union[str, None] = '01f93a40df71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'market_histories',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('type_id', sa.BigInteger(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('average', sa.Float(), nullable=True),
        sa.Column('highest', sa.Float(), nullable=True),
        sa.Column('lowest', sa.Float(), nullable=True),
        sa.Column('order_count', sa.BigInteger(), nullable=True),
        sa.Column('volume', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('region_id', 'type_id', 'date',
                            name='uq_market_histories_region_type_date'),
    )


def downgrade() -> None:
    op.drop_table('market_histories')
