"""Tests for evebs/routes/items.py."""
import pytest
from tests.factories import (
    make_universe_system, make_trade_hub, make_item, make_market_group,
    make_blueprint, make_jma,
)


class TestItemShow:
    def test_404_for_nonexistent_slug(self, client, db):
        resp = client.get('/items/does-not-exist')
        assert resp.status_code == 404

    def test_200_for_existing_slug(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        item = make_item(db, item_id=34, slug='tritanium')
        db.session.commit()

        resp = client.get('/items/tritanium')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data

    def test_item_found_by_numeric_id(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        item = make_item(db, item_id=34, slug='tritanium')
        db.session.commit()

        resp = client.get(f'/items/{item.id}')
        assert resp.status_code == 200


class TestItemManufacturingContext:
    def test_renders_materials_from_blueprint_tree(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        mat = make_item(db, item_id=34, slug='trit-items', name='Tritanium')
        crafted = make_item(db, item_id=35, slug='ammo-items', name='Ammo Items')
        bp = make_blueprint(db, crafted, prod_qtt=10)
        bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Tritanium', 'chain': {}}}
        make_jma(db, mat, min_sell_price=50.0)
        db.session.commit()

        resp = client.get('/items/ammo-items')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data

    def test_reaction_blueprint_with_user_industry_taxes(self, db, auth_client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        mat = make_item(db, item_id=34, slug='full-items', name='Fullerite')
        crafted = make_item(db, item_id=36, slug='c60-items', name='Blue Pill')
        bp = make_blueprint(db, crafted, prod_qtt=1)
        bp.activity_type = 'reaction'
        bp.manufacturing_tree = {'34': {'quantity': 10, 'name': 'Fullerite', 'chain': {}}}
        make_jma(db, mat, min_sell_price=100.0)
        db.session.commit()

        client, user = auth_client
        user.industry_taxes = {
            'reaction': {'system_cost_index': 5.0, 'scc_tax': 4.0, 'reaction_tax': 2.0}
        }
        db.session.commit()

        resp = client.get('/items/c60-items')
        assert resp.status_code == 200

