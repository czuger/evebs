"""Tests for evebs/routes/production_costs.py."""
import pytest

from tests.factories import make_item, make_blueprint, make_blueprint_material


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
        item = make_item(db, cpp_eve_item_id=99, slug='ammo', name='Fusion Charge S', base_item=False)
        db.session.commit()
        resp = client.get('/production_costs/ammo')
        assert resp.status_code == 200
        assert b'Fusion Charge S' in resp.data

    def test_200_for_crafted_item_with_blueprint(self, client, db):
        mat = make_item(db, cpp_eve_item_id=34, slug='trit', cost=10.0)
        crafted = make_item(db, cpp_eve_item_id=35, slug='ammo2')
        bp = make_blueprint(db, crafted)
        make_blueprint_material(db, bp, mat, required_qtt=3)
        db.session.commit()
        resp = client.get('/production_costs/ammo2')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data


class TestDailiesAvgPrices:
    def test_404_for_unknown_item(self, client, db):
        resp = client.get('/production_costs/nope/dailies_avg_prices/1')
        assert resp.status_code == 404

    def test_400_for_crafted_item(self, client, db):
        item = make_item(db, slug='crafted-item', base_item=False)
        db.session.commit()
        resp = client.get(f'/production_costs/crafted-item/dailies_avg_prices/1')
        assert resp.status_code == 400

    def test_200_for_base_item(self, client, db):
        from tests.factories import make_region, make_trade_hub
        region = make_region(db)
        hub = make_trade_hub(db, region)
        item = make_item(db, cpp_eve_item_id=36, slug='base-item', base_item=True)
        db.session.commit()
        resp = client.get(f'/production_costs/base-item/dailies_avg_prices/{hub.id}')
        assert resp.status_code == 200


class TestMarketHistories:
    def test_404_for_unknown_item(self, client, db):
        resp = client.get('/production_costs/nope/market_histories')
        assert resp.status_code == 404

    def test_200_for_existing_item(self, client, db):
        item = make_item(db, cpp_eve_item_id=37, slug='hist-item')
        db.session.commit()
        resp = client.get('/production_costs/hist-item/market_histories')
        assert resp.status_code == 200
