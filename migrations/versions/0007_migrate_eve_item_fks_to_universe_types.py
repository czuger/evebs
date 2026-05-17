"""migrate eve_item_id foreign keys from eve_items to universe_types

Revision ID: 0007_migrate_eve_item_fks
Revises: 0006_market_orders_source
Create Date: 2026-05-17

"""
from alembic import op
import sqlalchemy as sa

revision = '0007_migrate_eve_item_fks'
down_revision = '0006_market_orders_source'
branch_labels = None
depends_on = None

# Tables whose eve_item_id FK needs to change from eve_items.id → universe_types.id.
# Each entry: (table, fk_constraint_name, nullable)
_TABLES = [
    ('bpc_assets',                  'bpc_assets_eve_item_id_fkey',                  False),
    ('blueprint_materials',         'blueprint_materials_eve_item_id_fkey',          False),
    ('buy_orders_analytics',        'buy_orders_analytics_eve_item_id_fkey',         False),
    ('eve_market_histories_groups', 'eve_market_histories_groups_eve_item_id_fkey',  False),
    ('prices_advices',              'prices_advices_eve_item_id_fkey',               False),
    ('prices_mins',                 'prices_mins_eve_item_id_fkey',                  True),
    ('production_lists',            'production_lists_eve_item_id_fkey',             False),
    ('public_trade_orders',         'public_trade_orders_eve_item_id_fkey',          False),
    ('sales_finals',                'sales_finals_eve_item_id_fkey',                 False),
    ('user_sale_orders',            'user_sale_orders_eve_item_id_fkey',             False),
    ('weekly_price_details',        'weekly_price_details_eve_item_id_fkey',         False),
]

# The association table uses a different column name style
_EVE_ITEMS_USERS = ('eve_items_users', 'eve_items_users_eve_item_id_fkey')


def upgrade():
    for table, constraint, _ in _TABLES:
        op.drop_constraint(constraint, table, type_='foreignkey')
        op.create_foreign_key(constraint, table, 'universe_types', ['eve_item_id'], ['id'])

    table, constraint = _EVE_ITEMS_USERS
    op.drop_constraint(constraint, table, type_='foreignkey')
    op.create_foreign_key(constraint, table, 'universe_types', ['eve_item_id'], ['id'])


def downgrade():
    for table, constraint, _ in _TABLES:
        op.drop_constraint(constraint, table, type_='foreignkey')
        op.create_foreign_key(constraint, table, 'eve_items', ['eve_item_id'], ['id'])

    table, constraint = _EVE_ITEMS_USERS
    op.drop_constraint(constraint, table, type_='foreignkey')
    op.create_foreign_key(constraint, table, 'eve_items', ['eve_item_id'], ['id'])
