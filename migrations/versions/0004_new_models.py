"""add universe_categories, universe_groups, universe_types, market_orders; restructure market_groups

Revision ID: 0004_new_models
Revises: 0003_universe_no_cpp
Create Date: 2026-05-16

"""
from alembic import op
import sqlalchemy as sa

revision = '0004_new_models'
down_revision = '0003_universe_no_cpp'
branch_labels = None
depends_on = None


def upgrade():
    # --- Restructure market_groups (old cpp_ pattern → natural key) ---

    # Step 1: Drop FKs referencing market_groups
    op.drop_constraint('market_groups_parent_id_fkey', 'market_groups', type_='foreignkey')
    op.drop_constraint('eve_items_market_group_id_fkey', 'eve_items', type_='foreignkey')

    # Step 2: Data migration — translate FK values to cpp ids
    op.execute("""
        UPDATE market_groups child
        SET parent_id = parent.cpp_market_group_id
        FROM market_groups parent
        WHERE child.parent_id = parent.id
    """)
    op.execute("""
        UPDATE eve_items
        SET market_group_id = mg.cpp_market_group_id
        FROM market_groups mg
        WHERE eve_items.market_group_id = mg.id
    """)

    # Step 3: Swap PK — drop old auto-increment id, promote cpp_market_group_id → id
    op.execute('ALTER TABLE market_groups DROP CONSTRAINT market_groups_pkey CASCADE')
    op.execute('ALTER TABLE market_groups DROP COLUMN id')
    op.drop_constraint('market_groups_cpp_market_group_id_key', 'market_groups', type_='unique')
    op.execute('ALTER TABLE market_groups RENAME COLUMN cpp_market_group_id TO id')
    op.execute('ALTER TABLE market_groups ADD PRIMARY KEY (id)')

    # Step 4: Rename parent_id → parent_group_id
    op.execute('ALTER TABLE market_groups RENAME COLUMN parent_id TO parent_group_id')

    # Step 5: Drop old columns no longer in spec
    op.execute('ALTER TABLE market_groups DROP COLUMN cpp_parent_market_group_id')
    op.execute('ALTER TABLE market_groups DROP COLUMN created_at')
    op.execute('ALTER TABLE market_groups DROP COLUMN updated_at')

    # Step 6: Add description column
    op.execute("ALTER TABLE market_groups ADD COLUMN description TEXT NOT NULL DEFAULT ''")

    # Step 7: Alter name from varchar to text
    op.execute('ALTER TABLE market_groups ALTER COLUMN name TYPE TEXT')

    # Step 8: Alter eve_items.market_group_id from Integer to BigInteger
    op.execute('ALTER TABLE eve_items ALTER COLUMN market_group_id TYPE BIGINT')

    # Step 9: Re-add FKs
    op.create_foreign_key(
        'market_groups_parent_group_id_fkey',
        'market_groups', 'market_groups',
        ['parent_group_id'], ['id'],
    )
    op.create_foreign_key(
        'eve_items_market_group_id_fkey',
        'eve_items', 'market_groups',
        ['market_group_id'], ['id'],
    )

    # --- Create new tables ---

    op.create_table(
        'universe_categories',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('published', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'universe_groups',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('published', sa.Boolean(), nullable=False),
        sa.Column('category_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['universe_categories.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'universe_types',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('capacity', sa.Float(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('graphic_id', sa.BigInteger(), nullable=True),
        sa.Column('group_id', sa.BigInteger(), nullable=False),
        sa.Column('icon_id', sa.BigInteger(), nullable=True),
        sa.Column('market_group_id', sa.BigInteger(), nullable=True),
        sa.Column('mass', sa.Float(), nullable=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('packaged_volume', sa.Float(), nullable=True),
        sa.Column('portion_size', sa.BigInteger(), nullable=True),
        sa.Column('published', sa.Boolean(), nullable=False),
        sa.Column('radius', sa.Float(), nullable=True),
        sa.Column('volume', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['universe_groups.id']),
        sa.ForeignKeyConstraint(['market_group_id'], ['market_groups.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'market_orders',
        sa.Column('order_id', sa.BigInteger(), nullable=False),
        sa.Column('duration', sa.BigInteger(), nullable=False),
        sa.Column('is_buy_order', sa.Boolean(), nullable=False),
        sa.Column('issued', sa.DateTime(), nullable=False),
        sa.Column('location_id', sa.BigInteger(), nullable=False),
        sa.Column('min_volume', sa.BigInteger(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('range', sa.Text(), nullable=False),
        sa.Column('system_id', sa.BigInteger(), nullable=False),
        sa.Column('type_id', sa.BigInteger(), nullable=False),
        sa.Column('volume_remain', sa.BigInteger(), nullable=False),
        sa.Column('volume_total', sa.BigInteger(), nullable=True),
        sa.Column('source', sa.Enum('list_order_in_a_region', 'list_order_in_a_structure', name='market_order_source'), nullable=True),
        sa.ForeignKeyConstraint(['system_id'], ['universe_systems.id']),
        sa.ForeignKeyConstraint(['type_id'], ['universe_types.id']),
        sa.PrimaryKeyConstraint('order_id'),
    )


def downgrade():
    raise NotImplementedError('Downgrade not supported for this migration')
