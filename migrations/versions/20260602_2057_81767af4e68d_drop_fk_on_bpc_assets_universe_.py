"""drop FK on bpc_assets.universe_structure_id

Revision ID: 81767af4e68d
Revises: 000000000001
Create Date: 2026-06-02 20:57:10.083092

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '81767af4e68d'
down_revision: Union[str, None] = '000000000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('bpc_assets_universe_structure_id_fkey', 'bpc_assets', type_='foreignkey')


def downgrade() -> None:
    op.create_foreign_key(
        'bpc_assets_universe_structure_id_fkey',
        'bpc_assets', 'universe_structures',
        ['universe_structure_id'], ['id'],
    )
