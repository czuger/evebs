"""Tests for evebs/routes/components_to_buys.py."""
from tests.factories import (
    make_universe_region, make_universe_constellation,
    make_universe_system, make_trade_hub, make_universe_station,
    make_item, make_blueprint, make_jma, make_production_list, make_bpc_asset,
)


class TestComponentsToBuysShow:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/components_to_buys')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        resp = client.get('/components_to_buys')
        assert resp.status_code == 200

    def test_empty_list_renders(self, auth_client):
        client, _ = auth_client
        resp = client.get('/components_to_buys')
        assert b'Nothing to buy.' in resp.data


class TestComponentsToBuysCompute:
    def test_shows_materials_from_production_list(self, db, auth_client):
        client, user = auth_client
        system = make_universe_system(db)
        hub = make_trade_hub(db, system)
        mat = make_item(db, item_id=34, slug='trit-ctb', name='Tritanium')
        crafted = make_item(db, item_id=35, slug='ammo-ctb', name='Ammo CTB')
        bp = make_blueprint(db, crafted, prod_qtt=10)
        bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Tritanium', 'chain': {}}}
        make_jma(db, mat, min_sell_price=50.0)
        make_production_list(db, user, crafted, hub, runs_count=2)
        db.session.commit()

        resp = client.get('/components_to_buys')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data

    def test_station_filter_queries_bpc_assets(self, db, auth_client):
        client, user = auth_client
        ur = make_universe_region(db, region_id=10000099)
        uc = make_universe_constellation(db, ur, constellation_id=20000099)
        system = make_universe_system(db, uc, system_id=30000999, name='TestHub')
        hub = make_trade_hub(db, system)
        station = make_universe_station(db, system, station_id=60099999)
        mat = make_item(db, item_id=36, slug='pye-ctb', name='Pyerite')
        crafted = make_item(db, item_id=37, slug='charge-ctb', name='Charge CTB')
        bp = make_blueprint(db, crafted, prod_qtt=5)
        bp.manufacturing_tree = {'36': {'quantity': 50, 'name': 'Pyerite', 'chain': {}}}
        make_jma(db, mat, min_sell_price=10.0)
        make_production_list(db, user, crafted, hub, runs_count=1)
        make_bpc_asset(db, user, mat, station=station, quantity=20)
        db.session.commit()

        resp = client.get(f'/components_to_buys?station_id={station.id}')
        assert resp.status_code == 200
