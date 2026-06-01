"""blueprint_materials_indexes

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-24

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_blueprint_materials_blueprint_id', 'blueprint_materials', ['blueprint_id'])
    op.create_index('ix_blueprint_materials_eve_item_id',  'blueprint_materials', ['eve_item_id'])


def downgrade() -> None:
    op.drop_index('ix_blueprint_materials_blueprint_id', table_name='blueprint_materials', if_exists=True)
    op.drop_index('ix_blueprint_materials_eve_item_id',  table_name='blueprint_materials', if_exists=True)
