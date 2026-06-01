"""Drop legacy structures table and create universe_structures with new schema.

Revision ID: i3j4k5l6m7n8
Revises: h2i3j4k5l6m7
Create Date: 2026-06-01
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = 'i3j4k5l6m7n8'
down_revision = 'h2i3j4k5l6m7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table('structures')
    op.create_table(
        'universe_structures',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('type_id', sa.Integer(), nullable=True),
        sa.Column('universe_system_id', sa.BigInteger(), sa.ForeignKey('universe_systems.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
