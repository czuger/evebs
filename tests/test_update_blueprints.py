"""Tests for esi/update_blueprints.py.

The JSONL file path is patched with a temp file; all DB assertions run against
a real PostgreSQL test database (evebs_test).
"""
import json
from unittest.mock import patch

from evebs.extensions import db
from evebs.models import Blueprint, BlueprintMaterial, UniverseCategory, UniverseGroup, UniverseType
from esi.update_blueprints import update_blueprints


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_jsonl(tmp_path, records):
    p = tmp_path / 'blueprints.jsonl'
    p.write_text('\n'.join(json.dumps(r) for r in records) + '\n')
    return str(p)


def _seed_types(app, type_specs):
    """Seed one UniverseCategory + Group, then the given (id, name) types."""
    with app.app_context():
        db.session.add(UniverseCategory(id=1, name='Commodity', published=True))
        db.session.flush()
        db.session.add(UniverseGroup(id=1, name='Materials', published=True, category_id=1))
        db.session.flush()
        for type_id, name in type_specs:
            db.session.add(UniverseType(id=type_id, name=name, description='', published=True, group_id=1))
        db.session.commit()


_BP_RECORD = {
    'blueprintTypeID': 681,
    'activities': {
        'manufacturing': {
            'materials': [{'typeID': 38, 'quantity': 86}],
            'products': [{'typeID': 165, 'quantity': 1}],
            'time': 600,
        }
    },
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

import pytest


@pytest.fixture(autouse=True)
def clean_blueprint_tables(app):
    yield
    with app.app_context():
        db.session.query(BlueprintMaterial).delete()
        db.session.query(Blueprint).delete()
        db.session.query(UniverseType).delete()
        db.session.query(UniverseGroup).delete()
        db.session.query(UniverseCategory).delete()
        db.session.commit()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_inserts_blueprint_and_materials(app, tmp_path):
    _seed_types(app, [(165, 'Tritanium'), (38, 'Mexallon')])
    jsonl_path = _write_jsonl(tmp_path, [_BP_RECORD])

    with app.app_context():
        with patch('esi.update_blueprints.JSONL_PATH', jsonl_path):
            update_blueprints()

        bp = Blueprint.query.filter_by(id=681).first()
        assert bp is not None
        assert bp.produced_type_id == 165
        assert bp.prod_qtt == 1
        assert bp.nb_runs == 1
        assert bp.name == 'Tritanium'

        mats = BlueprintMaterial.query.filter_by(blueprint_id=681).all()
        assert len(mats) == 1
        assert mats[0].universe_type_id == 38
        assert mats[0].required_qtt == 86


def test_skips_non_manufacturing_blueprint(app, tmp_path):
    _seed_types(app, [(165, 'Tritanium')])
    record = {'blueprintTypeID': 999, 'activities': {'invention': {}}}
    jsonl_path = _write_jsonl(tmp_path, [record])

    with app.app_context():
        with patch('esi.update_blueprints.JSONL_PATH', jsonl_path):
            update_blueprints()

        assert Blueprint.query.count() == 0


def test_skips_blueprint_if_produced_type_unknown(app, tmp_path):
    _seed_types(app, [(38, 'Mexallon')])  # produced type 165 absent
    jsonl_path = _write_jsonl(tmp_path, [_BP_RECORD])

    with app.app_context():
        with patch('esi.update_blueprints.JSONL_PATH', jsonl_path):
            update_blueprints()

        assert Blueprint.query.count() == 0
        assert BlueprintMaterial.query.count() == 0


def test_skips_unknown_material_but_still_creates_blueprint(app, tmp_path):
    _seed_types(app, [(165, 'Tritanium')])  # material 38 absent
    jsonl_path = _write_jsonl(tmp_path, [_BP_RECORD])

    with app.app_context():
        with patch('esi.update_blueprints.JSONL_PATH', jsonl_path):
            update_blueprints()

        assert Blueprint.query.filter_by(id=681).first() is not None
        assert BlueprintMaterial.query.count() == 0


def test_second_run_replaces_all_records(app, tmp_path):
    _seed_types(app, [(165, 'Tritanium'), (38, 'Mexallon')])

    updated = {
        'blueprintTypeID': 681,
        'activities': {
            'manufacturing': {
                'materials': [{'typeID': 38, 'quantity': 200}],
                'products': [{'typeID': 165, 'quantity': 5}],
                'time': 600,
            }
        },
    }

    with app.app_context():
        with patch('esi.update_blueprints.JSONL_PATH', _write_jsonl(tmp_path, [_BP_RECORD])):
            update_blueprints()
        with patch('esi.update_blueprints.JSONL_PATH', _write_jsonl(tmp_path, [updated])):
            update_blueprints()

        assert Blueprint.query.count() == 1
        bp = Blueprint.query.filter_by(id=681).first()
        assert bp.prod_qtt == 5

        mats = BlueprintMaterial.query.filter_by(blueprint_id=681).all()
        assert len(mats) == 1
        assert mats[0].required_qtt == 200


def test_blueprint_name_from_universe_type(app, tmp_path):
    _seed_types(app, [(165, 'Tritanium'), (38, 'Mexallon')])
    jsonl_path = _write_jsonl(tmp_path, [_BP_RECORD])

    with app.app_context():
        with patch('esi.update_blueprints.JSONL_PATH', jsonl_path):
            update_blueprints()

        bp = Blueprint.query.filter_by(id=681).first()
        assert bp.name == 'Tritanium'


def test_schema_blueprints_has_produced_type_id(app):
    """Fails if migration 0011 hasn't been applied (column still named produced_cpp_type_id)."""
    with app.app_context():
        from sqlalchemy import inspect
        cols = {c['name'] for c in inspect(db.engine).get_columns('blueprints')}
        assert 'produced_type_id' in cols, "migration 0011 not applied: produced_type_id missing"
        assert 'produced_cpp_type_id' not in cols


def test_schema_blueprint_materials_has_universe_type_id(app):
    """Fails if migration 0011 hasn't been applied (column still named eve_item_id)."""
    with app.app_context():
        from sqlalchemy import inspect
        cols = {c['name'] for c in inspect(db.engine).get_columns('blueprint_materials')}
        assert 'universe_type_id' in cols, "migration 0011 not applied: universe_type_id missing"
        assert 'eve_item_id' not in cols



def test_skips_duplicate_produced_type_in_same_file(app, tmp_path):
    """Two blueprint IDs producing the same item must not cause a UniqueViolation."""
    _seed_types(app, [(165, 'Tritanium'), (38, 'Mexallon')])
    duplicate = {**_BP_RECORD, 'blueprintTypeID': 999}  # different BP id, same produced_type_id
    jsonl_path = _write_jsonl(tmp_path, [_BP_RECORD, duplicate])

    with app.app_context():
        with patch('esi.update_blueprints.JSONL_PATH', jsonl_path):
            update_blueprints()

        assert Blueprint.query.count() == 1
        assert Blueprint.query.filter_by(id=681).first() is not None


def test_multiple_blueprints_in_one_file(app, tmp_path):
    _seed_types(app, [(165, 'Tritanium'), (38, 'Mexallon'), (34, 'Pyerite'), (35, 'Isogen')])
    second = {
        'blueprintTypeID': 700,
        'activities': {
            'manufacturing': {
                'materials': [{'typeID': 35, 'quantity': 10}],
                'products': [{'typeID': 34, 'quantity': 2}],
                'time': 300,
            }
        },
    }
    jsonl_path = _write_jsonl(tmp_path, [_BP_RECORD, second])

    with app.app_context():
        with patch('esi.update_blueprints.JSONL_PATH', jsonl_path):
            update_blueprints()

        assert Blueprint.query.count() == 2
        assert BlueprintMaterial.query.count() == 2
