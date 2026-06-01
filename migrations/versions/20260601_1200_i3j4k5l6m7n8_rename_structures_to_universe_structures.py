"""Rename structures table to universe_structures, drop forbidden/orders_count_pages, add name/owner_id/type_id.

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
    op.drop_column('structures', 'forbidden')
    op.drop_column('structures', 'orders_count_pages')
    op.add_column('structures', sa.Column('name', sa.String(), nullable=False, server_default=''))
    op.alter_column('structures', 'name', server_default=None)
    op.add_column('structures', sa.Column('owner_id', sa.Integer(), nullable=False, server_default='0'))
    op.alter_column('structures', 'owner_id', server_default=None)
    op.add_column('structures', sa.Column('type_id', sa.Integer(), nullable=True))
    op.rename_table('structures', 'universe_structures')


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
