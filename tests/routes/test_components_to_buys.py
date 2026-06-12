"""Tests for evebs/routes/components_to_buys.py."""
from tests.factories import (
    make_universe_region, make_universe_constellation,
    make_universe_system, make_trade_hub, make_universe_station,
    make_item, make_blueprint, make_jita_min_price, make_production_list, make_user_asset,
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
        make_jita_min_price(db, mat, min_sell_price=50.0)
        make_production_list(db, user, crafted, hub, runs_count=2)
        db.session.commit()

        resp = client.get('/components_to_buys')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data
        assert b'Total required volume' in resp.data

    def test_tech2_blueprint_gets_2pct_material_reduction(self, db, auth_client):
        """A Tech II blueprint (invented) consumes 2% fewer materials; T1 is unchanged."""
        from evebs.routes.components_to_buys import _compute_components
        _, user = auth_client

        system = make_universe_system(db)
        hub = make_trade_hub(db, system)
        make_item(db, item_id=34, slug='trit-t2', name='Tritanium')

        t2 = make_item(db, item_id=35, slug='ammo-ii', name='Ammo II')
        t2_bp = make_blueprint(db, t2, blueprint_id=35001, prod_qtt=10)
        t2_bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Tritanium', 'chain': {}}}
        t2_bp.is_invented_from_id = 99999          # marks it Tech II

        t1 = make_item(db, item_id=36, slug='ammo-i', name='Ammo I')
        t1_bp = make_blueprint(db, t1, blueprint_id=36001, prod_qtt=10)
        t1_bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Tritanium', 'chain': {}}}

        make_production_list(db, user, t2, hub, runs_count=2)
        make_production_list(db, user, t1, hub, runs_count=2)
        db.session.commit()

        rows = {r.eve_item_id: r for r in _compute_components(user)}
        # T2: ceil(100 * 2 * 0.98) = 196 ; T1: 100 * 2 = 200 ; aggregated across both = 396
        assert rows[34].qtt_to_buy == 396

    def test_reaction_applies_material_consumption(self, db, auth_client):
        """A reaction-list entry reduces materials by the user's material_consumption modifier."""
        from evebs.routes.components_to_buys import _compute_components
        from tests.factories import make_item as _mk
        from evebs.models import ReactionList
        _, user = auth_client
        user.reaction_modifications = {'system_cost_index': 5, 'scc_tax': 4,
                                       'reaction_tax': 1, 'material_consumption': -2}

        mat = _mk(db, item_id=34, slug='hydro', name='Hydrogen')
        prod = _mk(db, item_id=16679, slug='fullerides', name='Fullerides')
        bp = make_blueprint(db, prod, blueprint_id=46209, prod_qtt=3000)
        bp.activity_type = 'reaction'
        bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Hydrogen', 'chain': {}}}
        make_jita_min_price(db, mat, min_sell_price=5.0)
        db.session.add(ReactionList(user_id=user.id, eve_item_id=prod.id, runs_count=2))
        db.session.commit()

        rows = {r.eve_item_id: r for r in _compute_components(user)}
        # ceil(100 * 2 * (1 + (-2)/100)) = ceil(200 * 0.98) = 196
        assert rows[34].qtt_to_buy == 196

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
        make_jita_min_price(db, mat, min_sell_price=10.0)
        make_production_list(db, user, crafted, hub, runs_count=1)
        make_user_asset(db, user, mat, station=station, quantity=20)
        db.session.commit()

        resp = client.get(f'/components_to_buys?station_id={station.id}')
        assert resp.status_code == 200
