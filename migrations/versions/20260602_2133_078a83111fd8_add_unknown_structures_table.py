"""add unknown_structures table

Revision ID: 078a83111fd8
Revises: 81767af4e68d
Create Date: 2026-06-02 21:33:45.258663

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '078a83111fd8'
down_revision: Union[str, None] = '81767af4e68d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'unknown_structures',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('unknown_structures')
