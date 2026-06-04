"""Tests for evebs/routes/production_costs.py."""
import pytest

from tests.factories import make_item, make_blueprint


class TestProductionCostsShow:
    def test_404_for_unknown_slug(self, client, db):
        resp = client.get('/production_costs/does-not-exist')
        assert resp.status_code == 404

    def test_400_for_base_item(self, client, db):
        item = make_item(db, slug='trit-base', base_item=True)
        db.session.commit()
        resp = client.get('/production_costs/trit-base')
        assert resp.status_code == 400

    def test_200_for_crafted_item_without_blueprint(self, client, db):
        item = make_item(db, item_id=99, slug='ammo', name='Fusion Charge S', base_item=False)
        db.session.commit()
        resp = client.get('/production_costs/ammo')
        assert resp.status_code == 200
        assert b'Fusion Charge S' in resp.data

    def test_200_for_crafted_item_with_blueprint(self, client, db):
        crafted = make_item(db, item_id=35, slug='ammo2')
        make_blueprint(db, crafted, manufacturing_cost=50.0)
        db.session.commit()
        resp = client.get('/production_costs/ammo2')
        assert resp.status_code == 200
