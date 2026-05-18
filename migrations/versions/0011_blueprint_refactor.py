"""Blueprint model refactor: natural PK, rename fields, BigInteger ids

Revision ID: 0011_blueprint_refactor
Revises: 0010_trade_hub_idx
Create Date: 2026-05-18

"""
from alembic import op

revision = '0011_blueprint_refactor'
down_revision = '0010_trade_hub_idx'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE blueprints RENAME COLUMN produced_cpp_type_id TO produced_type_id;
        ALTER TABLE blueprint_materials RENAME COLUMN eve_item_id TO universe_type_id;

        ALTER TABLE blueprints ALTER COLUMN produced_type_id TYPE BIGINT;
        ALTER TABLE blueprint_materials ALTER COLUMN id TYPE BIGINT;
        ALTER TABLE blueprint_materials ALTER COLUMN blueprint_id TYPE BIGINT;
        ALTER TABLE blueprint_materials ALTER COLUMN required_qtt TYPE BIGINT;

        ALTER TABLE blueprint_materials DROP CONSTRAINT blueprint_materials_blueprint_id_fkey;
        ALTER TABLE blueprint_modifications DROP CONSTRAINT blueprint_modifications_blueprint_id_fkey;
        ALTER TABLE eve_items DROP CONSTRAINT eve_items_blueprint_id_fkey;

        ALTER TABLE blueprints ADD COLUMN new_id BIGINT;
        UPDATE blueprints SET new_id = cpp_blueprint_id;

        ALTER TABLE blueprint_materials ADD COLUMN new_blueprint_id BIGINT;
        UPDATE blueprint_materials SET new_blueprint_id = b.new_id
          FROM blueprints b WHERE blueprint_materials.blueprint_id = b.id;

        ALTER TABLE blueprint_modifications ADD COLUMN new_blueprint_id BIGINT;
        UPDATE blueprint_modifications SET new_blueprint_id = b.new_id
          FROM blueprints b WHERE blueprint_modifications.blueprint_id = b.id;

        ALTER TABLE eve_items ADD COLUMN new_blueprint_id BIGINT;
        UPDATE eve_items SET new_blueprint_id = b.new_id
          FROM blueprints b WHERE eve_items.blueprint_id = b.id;

        ALTER TABLE blueprints DROP CONSTRAINT blueprints_pkey;
        ALTER TABLE blueprints DROP COLUMN id;
        ALTER TABLE blueprints DROP COLUMN cpp_blueprint_id;
        ALTER TABLE blueprints RENAME COLUMN new_id TO id;
        ALTER TABLE blueprints ADD PRIMARY KEY (id);

        ALTER TABLE blueprint_materials DROP COLUMN blueprint_id;
        ALTER TABLE blueprint_materials RENAME COLUMN new_blueprint_id TO blueprint_id;
        ALTER TABLE blueprint_materials ALTER COLUMN blueprint_id SET NOT NULL;
        ALTER TABLE blueprint_materials ADD CONSTRAINT blueprint_materials_blueprint_id_fkey
          FOREIGN KEY (blueprint_id) REFERENCES blueprints(id);

        ALTER TABLE blueprint_modifications DROP COLUMN blueprint_id;
        ALTER TABLE blueprint_modifications RENAME COLUMN new_blueprint_id TO blueprint_id;
        ALTER TABLE blueprint_modifications ALTER COLUMN blueprint_id SET NOT NULL;
        ALTER TABLE blueprint_modifications ADD CONSTRAINT blueprint_modifications_blueprint_id_fkey
          FOREIGN KEY (blueprint_id) REFERENCES blueprints(id);

        ALTER TABLE eve_items DROP COLUMN blueprint_id;
        ALTER TABLE eve_items RENAME COLUMN new_blueprint_id TO blueprint_id;
        ALTER TABLE eve_items ADD CONSTRAINT eve_items_blueprint_id_fkey
          FOREIGN KEY (blueprint_id) REFERENCES blueprints(id);
    """)


def downgrade():
    raise NotImplementedError('Downgrade not supported for this migration.')
