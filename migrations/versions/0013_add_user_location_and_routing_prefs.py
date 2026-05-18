"""add user_location_station_id, avoid_low_sec, avoid_null_sec, max_jumps to users

Revision ID: 0013_user_location_routing
Revises: 0012_add_cost_indices
Create Date: 2026-05-18

"""
from alembic import op
import sqlalchemy as sa

revision = '0013_user_location_routing'
down_revision = '0012_add_cost_indices'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('user_location_station_id', sa.BigInteger(),
                                     nullable=True))
    op.create_foreign_key(
        'users_user_location_station_id_fkey',
        'users', 'universe_stations',
        ['user_location_station_id'], ['id'],
    )
    op.add_column('users', sa.Column('avoid_low_sec', sa.Boolean(),
                                     nullable=False, server_default='false'))
    op.add_column('users', sa.Column('avoid_null_sec', sa.Boolean(),
                                     nullable=False, server_default='false'))
    op.add_column('users', sa.Column('max_jumps', sa.Integer(),
                                     nullable=False, server_default='5'))


def downgrade():
    op.drop_constraint('users_user_location_station_id_fkey', 'users', type_='foreignkey')
    op.drop_column('users', 'user_location_station_id')
    op.drop_column('users', 'avoid_low_sec')
    op.drop_column('users', 'avoid_null_sec')
    op.drop_column('users', 'max_jumps')
