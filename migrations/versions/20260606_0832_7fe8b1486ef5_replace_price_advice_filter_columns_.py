"""replace price advice filter columns with sell_orders_filtering jsonb

Revision ID: 7fe8b1486ef5
Revises: b02331e544da
Create Date: 2026-06-06 08:32:17.696774

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '7fe8b1486ef5'
down_revision: Union[str, None] = 'b02331e544da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column(
        'sell_orders_filtering',
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=False,
        server_default='{"min_margin_percent": 20, "min_batch_margin_amount": 5000000}',
    ))
    op.execute("""
        UPDATE users
        SET sell_orders_filtering = jsonb_build_object(
            'min_margin_percent',     min_pcent_for_advice,
            'min_batch_margin_amount', min_amount_for_advice
        )
    """)
    op.drop_column('users', 'vol_month_pcent')
    op.drop_column('users', 'min_pcent_for_advice')
    op.drop_column('users', 'min_amount_for_advice')


def downgrade() -> None:
    op.add_column('users', sa.Column('min_amount_for_advice', sa.Integer(), nullable=False, server_default='5000000'))
    op.add_column('users', sa.Column('min_pcent_for_advice', sa.Integer(), nullable=False, server_default='20'))
    op.add_column('users', sa.Column('vol_month_pcent', sa.Integer(), nullable=False, server_default='5'))
    op.execute("""
        UPDATE users
        SET min_pcent_for_advice  = (sell_orders_filtering->>'min_margin_percent')::int,
            min_amount_for_advice = (sell_orders_filtering->>'min_batch_margin_amount')::int
    """)
    op.drop_column('users', 'sell_orders_filtering')
