"""fix reaction blueprint ids to reaction formula type

Revision ID: 307283ad699f
Revises: ca692be09df0
Create Date: 2026-06-12 20:12:16.097248

Reaction Blueprint rows were keyed by their produced (product) type id instead of the
reaction-formula type id (e.g. Fullerides 16679 instead of Fullerides Reaction Formula
46209). Re-key them to the formula type id. The three FKs to blueprints.id are recreated
with ON UPDATE CASCADE so a single UPDATE of the primary key repoints eve_items,
user_blueprints and blueprint_modifications automatically.
"""
import json
import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '307283ad699f'
down_revision: Union[str, None] = 'ca692be09df0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BLUEPRINTS_JSONL = os.path.join(
    os.path.dirname(__file__), '..', '..', 'data', 'eve_static_data', 'blueprints.jsonl')

# (constraint name, child table, child column) for every FK referencing blueprints.id.
_FKS = [
    ('eve_items_blueprint_id_fkey', 'eve_items', 'blueprint_id'),
    ('user_blueprints_blueprint_id_fkey', 'user_blueprints', 'blueprint_id'),
    ('blueprint_modifications_blueprint_id_fkey', 'blueprint_modifications', 'blueprint_id'),
]


def _prod_to_formula():
    """produced_type_id → reaction-formula type id (the blueprint `_key`) from the SDE."""
    mapping = {}
    with open(BLUEPRINTS_JSONL) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            rxn = obj.get('activities', {}).get('reaction')
            if rxn and rxn.get('products'):
                mapping[rxn['products'][0]['typeID']] = obj['_key']
    return mapping


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Recreate the FKs with ON UPDATE CASCADE (keep ON DELETE NO ACTION).
    for name, table, col in _FKS:
        conn.execute(sa.text(f'ALTER TABLE {table} DROP CONSTRAINT {name}'))
        conn.execute(sa.text(
            f'ALTER TABLE {table} ADD CONSTRAINT {name} '
            f'FOREIGN KEY ({col}) REFERENCES blueprints (id) ON UPDATE CASCADE'))

    # 2. Re-key each reaction blueprint that is still keyed by its product type id.
    prod_to_formula = _prod_to_formula()
    wrong = conn.execute(sa.text(
        "SELECT id, produced_type_id FROM blueprints "
        "WHERE activity_type = 'reaction' AND id = produced_type_id")).all()

    rekeyed = 0
    for old_id, produced in wrong:
        formula = prod_to_formula.get(produced)
        if formula is None or formula == old_id:
            continue
        clash = conn.execute(sa.text('SELECT 1 FROM blueprints WHERE id = :f'),
                             {'f': formula}).first()
        if clash:
            continue
        conn.execute(sa.text(
            'UPDATE blueprints '
            'SET id = :formula, '
            '    name = COALESCE((SELECT name FROM eve_items WHERE id = :formula), name) '
            'WHERE id = :old'),
            {'formula': formula, 'old': old_id})
        rekeyed += 1

    print(f'Re-keyed {rekeyed} reaction blueprints to their formula type id.')


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
