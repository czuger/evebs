"""Replace batch_cap and batch_cap_multiplier with buy_order_filtering jsonb

Revision ID: 450b44c06b76
Revises: 9c9de23a97d3
Create Date: 2026-06-07 20:29:08.694219

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '450b44c06b76'
down_revision: Union[str, None] = '9c9de23a97d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column(
        'buy_order_filtering',
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=False,
        server_default='{"batch_cap": true, "batch_cap_multiplier": 10, "min_margin_percent": 20, "min_batch_margin_amount": 5000000}',
    ))
    op.execute("""
        UPDATE users
        SET buy_order_filtering = jsonb_build_object(
            'batch_cap',              batch_cap,
            'batch_cap_multiplier',   batch_cap_multiplier,
            'min_margin_percent',     20,
            'min_batch_margin_amount', 5000000
        )
    """)
    op.drop_column('users', 'batch_cap')
    op.drop_column('users', 'batch_cap_multiplier')


def downgrade() -> None:
    op.add_column('users', sa.Column('batch_cap', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('batch_cap_multiplier', sa.Integer(), nullable=False, server_default='10'))
    op.execute("""
        UPDATE users
        SET batch_cap            = (buy_order_filtering->>'batch_cap')::boolean,
            batch_cap_multiplier = (buy_order_filtering->>'batch_cap_multiplier')::int
    """)
    op.drop_column('users', 'buy_order_filtering')
