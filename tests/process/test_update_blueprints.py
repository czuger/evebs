import json
import pytest

from tests.factories import make_item, make_blueprint, make_jita_min_price


def _write_blueprints_jsonl(path, entries):
    path.write_text('\n'.join(json.dumps(e) for e in entries) + '\n')


def _invent_entry(blueprint_type_id, mfg_type_id, invention_blueprint_type_ids):
    """T1 blueprint entry: manufactures mfg_type_id, invents the given T2 blueprint type IDs."""
    return {
        '_key': blueprint_type_id,
        'activities': {
            'manufacturing': {
                'products': [{'typeID': mfg_type_id, 'quantity': 1}],
            },
            'invention': {
                'products': [{'typeID': t, 'quantity': 1} for t in invention_blueprint_type_ids],
            },
        },
    }


def _mfg_entry(blueprint_type_id, produces_type_id):
    """Plain manufacturing-only entry (e.g. the T2 blueprint item produced by invention)."""
    return {
        '_key': blueprint_type_id,
        'activities': {
            'manufacturing': {
                'products': [{'typeID': produces_type_id, 'quantity': 1}],
            },
        },
    }


# ---------------------------------------------------------------------------
# refresh_blueprint_manufacturing_costs
# ---------------------------------------------------------------------------

class TestRefreshBlueprintManufacturingCosts:
    def test_updates_cost_when_prices_exist(self, db):
        mat = make_item(db, item_id=34, name='Tritanium', slug='tritanium')
        item = make_item(db, item_id=100, name='Widget', slug='widget')
        bp = make_blueprint(db, item)
        bp.manufacturing_tree = {'34': {'name': 'Tritanium', 'quantity': 10, 'chain': {}}}
        make_jita_min_price(db, mat, min_sell_price=500.0)
        db.session.commit()

        from process.update_blueprints import refresh_blueprint_manufacturing_costs
        result = refresh_blueprint_manufacturing_costs()

        db.session.refresh(bp)
        assert bp.manufacturing_cost == pytest.approx(5000.0)
        assert result['updated'] == 1
        assert result['no_price'] == 0

    def test_sets_null_when_material_price_missing(self, db):
        make_item(db, item_id=34, name='Tritanium', slug='tritanium')
        item = make_item(db, item_id=100, name='Widget', slug='widget')
        bp = make_blueprint(db, item)
        bp.manufacturing_tree = {'34': {'name': 'Tritanium', 'quantity': 10, 'chain': {}}}
        # No JMA row → price missing
        db.session.commit()

        from process.update_blueprints import refresh_blueprint_manufacturing_costs
        result = refresh_blueprint_manufacturing_costs()

        db.session.refresh(bp)
        assert bp.manufacturing_cost is None
        assert result['no_price'] == 1
        assert result['updated'] == 0

    def test_skips_blueprint_without_tree(self, db):
        item = make_item(db, item_id=100, name='Widget', slug='widget')
        bp = make_blueprint(db, item)
        bp.manufacturing_tree = None
        db.session.commit()

        from process.update_blueprints import refresh_blueprint_manufacturing_costs
        result = refresh_blueprint_manufacturing_costs()

        assert result['updated'] == 0
        assert result['no_price'] == 0

    def test_multiple_materials(self, db):
        mat1 = make_item(db, item_id=34, name='Tritanium', slug='tritanium')
        mat2 = make_item(db, item_id=35, name='Pyerite',   slug='pyerite')
        item = make_item(db, item_id=100, name='Widget', slug='widget')
        bp = make_blueprint(db, item)
        bp.manufacturing_tree = {
            '34': {'name': 'Tritanium', 'quantity': 10, 'chain': {}},
            '35': {'name': 'Pyerite',   'quantity': 5,  'chain': {}},
        }
        make_jita_min_price(db, mat1, min_sell_price=100.0)
        make_jita_min_price(db, mat2, min_sell_price=200.0)
        db.session.commit()

        from process.update_blueprints import refresh_blueprint_manufacturing_costs
        refresh_blueprint_manufacturing_costs()

        db.session.refresh(bp)
        assert bp.manufacturing_cost == pytest.approx(10 * 100.0 + 5 * 200.0)


# ---------------------------------------------------------------------------
# upsert_blueprints — create-path uses the blueprint-type id, not the product id
# ---------------------------------------------------------------------------

class TestUpsertBlueprintsCreatePath:
    def test_reaction_created_with_formula_type_id(self, db):
        """A new reaction blueprint is keyed by its reaction-formula type id (not the product)."""
        product = make_item(db, item_id=16679, name='Fullerides', slug='fullerides')
        formula = make_item(db, item_id=46209, name='Fullerides Reaction Formula',
                            slug='fullerides-reaction-formula')
        db.session.commit()

        tree = {'16679': {'name': 'Fullerides', 'activity_type': 'reaction',
                          'manufacturing_level': 1, 'prod_qty': 3000, 'chain': {}}}
        item_map = {16679: product, 46209: formula}

        from process.update_blueprints import upsert_blueprints
        from evebs.models import Blueprint
        new, updated, _ = upsert_blueprints(
            tree, item_map, price_map={}, bp_map={}, bp_type_map={16679: 46209})
        db.session.commit()

        assert new == 1 and updated == 0
        bp = db.session.get(Blueprint, 46209)
        assert bp is not None
        assert bp.produced_type_id == 16679
        assert bp.name == 'Fullerides Reaction Formula'
        assert db.session.get(Blueprint, 16679) is None        # not keyed by the product
        db.session.refresh(product)
        assert product.blueprint_id == 46209


# ---------------------------------------------------------------------------
# update_invented_from
#
# In the EVE SDE, invention.products[].typeID is the T2 BLUEPRINT item typeID
# (e.g. "Hail Blueprint"), NOT the typeID of the item it produces ("Hail").
# update_invented_from resolves this via a first pass that maps blueprint item
# typeID → produced item typeID.
#
# Test IDs used below:
#   T1 blueprint item: 1001  produces T1 item: 100  (e.g. Barrage M Blueprint)
#   T2 blueprint item: 2001  produces T2 item: 200  (e.g. Hail M Blueprint)
# ---------------------------------------------------------------------------

class TestUpdateInventedFrom:
    def test_sets_is_invented_from_id(self, db, tmp_path, monkeypatch):
        t1_item = make_item(db, item_id=100, name='Barrage M', slug='barrage-m')
        t2_item = make_item(db, item_id=200, name='Hail M',    slug='hail-m')
        t1_bp   = make_blueprint(db, t1_item, blueprint_id=100)
        t2_bp   = make_blueprint(db, t2_item, blueprint_id=200)
        db.session.commit()

        jsonl = tmp_path / 'blueprints.jsonl'
        _write_blueprints_jsonl(jsonl, [
            _invent_entry(1001, 100, [2001]),  # T1 blueprint → makes 100, invents T2 bp 2001
            _mfg_entry(2001, 200),              # T2 blueprint → makes 200
        ])
        monkeypatch.setattr('process.update_blueprints.BLUEPRINTS_JSONL', str(jsonl))

        from process.update_blueprints import update_invented_from
        bp_map = {100: t1_bp, 200: t2_bp}
        count = update_invented_from(bp_map)

        db.session.refresh(t2_bp)
        assert t2_bp.is_invented_from_id == 100
        assert count == 1

    def test_t1_is_not_modified(self, db, tmp_path, monkeypatch):
        t1_item = make_item(db, item_id=100, name='Barrage M', slug='barrage-m')
        t2_item = make_item(db, item_id=200, name='Hail M',    slug='hail-m')
        t1_bp   = make_blueprint(db, t1_item, blueprint_id=100)
        t2_bp   = make_blueprint(db, t2_item, blueprint_id=200)
        db.session.commit()

        jsonl = tmp_path / 'blueprints.jsonl'
        _write_blueprints_jsonl(jsonl, [
            _invent_entry(1001, 100, [2001]),
            _mfg_entry(2001, 200),
        ])
        monkeypatch.setattr('process.update_blueprints.BLUEPRINTS_JSONL', str(jsonl))

        from process.update_blueprints import update_invented_from
        update_invented_from({100: t1_bp, 200: t2_bp})

        db.session.refresh(t1_bp)
        assert t1_bp.is_invented_from_id is None

    def test_skips_when_t1_not_in_bp_map(self, db, tmp_path, monkeypatch):
        """T1 blueprint not in DB → T2 is_invented_from_id stays NULL."""
        t2_item = make_item(db, item_id=200, name='Hail M', slug='hail-m')
        t2_bp   = make_blueprint(db, t2_item, blueprint_id=200)
        db.session.commit()

        jsonl = tmp_path / 'blueprints.jsonl'
        _write_blueprints_jsonl(jsonl, [
            _invent_entry(1001, 100, [2001]),  # T1 item 100 has no Blueprint row in DB
            _mfg_entry(2001, 200),
        ])
        monkeypatch.setattr('process.update_blueprints.BLUEPRINTS_JSONL', str(jsonl))

        from process.update_blueprints import update_invented_from
        count = update_invented_from({200: t2_bp})  # bp_map has no entry for 100

        assert count == 0
        db.session.refresh(t2_bp)
        assert t2_bp.is_invented_from_id is None

    def test_skips_t2_item_not_in_bp_map(self, db, tmp_path, monkeypatch):
        t1_item = make_item(db, item_id=100, name='Barrage M', slug='barrage-m')
        t1_bp   = make_blueprint(db, t1_item, blueprint_id=100)
        db.session.commit()

        jsonl = tmp_path / 'blueprints.jsonl'
        _write_blueprints_jsonl(jsonl, [
            _invent_entry(1001, 100, [2001]),
            _mfg_entry(2001, 200),  # T2 bp resolves to item 200, but 200 is not in bp_map
        ])
        monkeypatch.setattr('process.update_blueprints.BLUEPRINTS_JSONL', str(jsonl))

        from process.update_blueprints import update_invented_from
        count = update_invented_from({100: t1_bp})  # 200 absent
        assert count == 0

    def test_skips_t2_blueprint_with_no_mfg_entry(self, db, tmp_path, monkeypatch):
        t1_item = make_item(db, item_id=100, name='Barrage M', slug='barrage-m')
        t2_item = make_item(db, item_id=200, name='Hail M',    slug='hail-m')
        t1_bp   = make_blueprint(db, t1_item, blueprint_id=100)
        t2_bp   = make_blueprint(db, t2_item, blueprint_id=200)
        db.session.commit()

        jsonl = tmp_path / 'blueprints.jsonl'
        # T2 blueprint item 2001 has no manufacturing entry → can't resolve produced ID
        _write_blueprints_jsonl(jsonl, [_invent_entry(1001, 100, [2001])])
        monkeypatch.setattr('process.update_blueprints.BLUEPRINTS_JSONL', str(jsonl))

        from process.update_blueprints import update_invented_from
        count = update_invented_from({100: t1_bp, 200: t2_bp})
        assert count == 0

        db.session.refresh(t2_bp)
        assert t2_bp.is_invented_from_id is None

    def test_skips_entry_without_manufacturing_activity(self, db, tmp_path, monkeypatch):
        t2_item = make_item(db, item_id=200, name='Hail M', slug='hail-m')
        t2_bp   = make_blueprint(db, t2_item, blueprint_id=200)
        db.session.commit()

        # Entry has only invention, no manufacturing → skipped
        entry = {
            '_key': 1001,
            'activities': {
                'invention': {'products': [{'typeID': 2001}]},
            },
        }
        jsonl = tmp_path / 'blueprints.jsonl'
        _write_blueprints_jsonl(jsonl, [entry, _mfg_entry(2001, 200)])
        monkeypatch.setattr('process.update_blueprints.BLUEPRINTS_JSONL', str(jsonl))

        from process.update_blueprints import update_invented_from
        count = update_invented_from({200: t2_bp})
        assert count == 0

        db.session.refresh(t2_bp)
        assert t2_bp.is_invented_from_id is None

    def test_dry_run_does_not_write(self, db, tmp_path, monkeypatch):
        t1_item = make_item(db, item_id=100, name='Barrage M', slug='barrage-m')
        t2_item = make_item(db, item_id=200, name='Hail M',    slug='hail-m')
        t1_bp   = make_blueprint(db, t1_item, blueprint_id=100)
        t2_bp   = make_blueprint(db, t2_item, blueprint_id=200)
        db.session.commit()

        jsonl = tmp_path / 'blueprints.jsonl'
        _write_blueprints_jsonl(jsonl, [
            _invent_entry(1001, 100, [2001]),
            _mfg_entry(2001, 200),
        ])
        monkeypatch.setattr('process.update_blueprints.BLUEPRINTS_JSONL', str(jsonl))

        from process.update_blueprints import update_invented_from
        count = update_invented_from({100: t1_bp, 200: t2_bp}, dry_run=True)

        assert count == 1
        db.session.refresh(t2_bp)
        assert t2_bp.is_invented_from_id is None

    def test_one_t1_invents_multiple_t2(self, db, tmp_path, monkeypatch):
        t1_item  = make_item(db, item_id=100, name='Condor',  slug='condor')
        t2a_item = make_item(db, item_id=201, name='Raptor',  slug='raptor')
        t2b_item = make_item(db, item_id=202, name='Crow',    slug='crow')
        t1_bp    = make_blueprint(db, t1_item,  blueprint_id=100)
        t2a_bp   = make_blueprint(db, t2a_item, blueprint_id=201)
        t2b_bp   = make_blueprint(db, t2b_item, blueprint_id=202)
        db.session.commit()

        jsonl = tmp_path / 'blueprints.jsonl'
        _write_blueprints_jsonl(jsonl, [
            _invent_entry(1001, 100, [2001, 2002]),  # T1 invents two T2 blueprints
            _mfg_entry(2001, 201),                   # T2 bp 2001 → Raptor (201)
            _mfg_entry(2002, 202),                   # T2 bp 2002 → Crow (202)
        ])
        monkeypatch.setattr('process.update_blueprints.BLUEPRINTS_JSONL', str(jsonl))

        from process.update_blueprints import update_invented_from
        count = update_invented_from({100: t1_bp, 201: t2a_bp, 202: t2b_bp})

        assert count == 2
        db.session.refresh(t2a_bp)
        db.session.refresh(t2b_bp)
        assert t2a_bp.is_invented_from_id == 100
        assert t2b_bp.is_invented_from_id == 100
