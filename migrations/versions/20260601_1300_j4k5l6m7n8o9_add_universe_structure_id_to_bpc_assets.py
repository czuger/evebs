"""Add universe_structure_id FK to bpc_assets.

Revision ID: j4k5l6m7n8o9
Revises: i3j4k5l6m7n8
Create Date: 2026-06-01
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = 'j4k5l6m7n8o9'
down_revision = 'i3j4k5l6m7n8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('bpc_assets', sa.Column('universe_structure_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        'fk_bpc_assets_universe_structure_id',
        'bpc_assets', 'universe_structures',
        ['universe_structure_id'], ['id'],
    )


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
