"""Tests for evebs/routes/components_to_buys.py."""
from tests.factories import (
    make_universe_region, make_universe_constellation,
    make_universe_system, make_trade_hub, make_universe_station,
    make_item, make_blueprint, make_jita_min_price, make_production_list, make_user_asset,
)


PRODUCTION_URL = '/components_to_buys_for_production'
REACTION_URL = '/components_to_buys_for_reaction'


class TestComponentsToBuysShow:
    def test_redirects_unauthenticated(self, client):
        assert client.get(PRODUCTION_URL).status_code == 302
        assert client.get(REACTION_URL).status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        assert client.get(PRODUCTION_URL).status_code == 200
        assert client.get(REACTION_URL).status_code == 200

    def test_empty_list_renders(self, auth_client):
        client, _ = auth_client
        assert b'Nothing to buy.' in client.get(PRODUCTION_URL).data
        assert b'Nothing to buy.' in client.get(REACTION_URL).data


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

        resp = client.get(PRODUCTION_URL)
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data
        assert b'Totals' in resp.data

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

        rows = {r.eve_item_id: r for r in _compute_components(user, 'production')}
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

        rows = {r.eve_item_id: r for r in _compute_components(user, 'reaction')}
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

        resp = client.get(f'{PRODUCTION_URL}?station_id={station.id}')
        assert resp.status_code == 200


class TestComponentsToBuysActivityIsolation:
    def _seed_one_of_each(self, db, user):
        from evebs.models import ReactionList
        system = make_universe_system(db)
        hub = make_trade_hub(db, system)
        pmat = make_item(db, item_id=34, slug='trit-iso', name='Tritanium')
        pcraft = make_item(db, item_id=35, slug='ammo-iso', name='Ammo Iso')
        pbp = make_blueprint(db, pcraft, blueprint_id=35010, prod_qtt=10)
        pbp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Tritanium', 'chain': {}}}
        make_jita_min_price(db, pmat, min_sell_price=5.0)
        make_production_list(db, user, pcraft, hub, runs_count=1)

        rmat = make_item(db, item_id=16634, slug='hydro-iso', name='Hydrogen Iso')
        rprod = make_item(db, item_id=16679, slug='fuller-iso', name='Fullerides Iso')
        rbp = make_blueprint(db, rprod, blueprint_id=46210, prod_qtt=3000)
        rbp.activity_type = 'reaction'
        rbp.manufacturing_tree = {'16634': {'quantity': 100, 'name': 'Hydrogen Iso', 'chain': {}}}
        make_jita_min_price(db, rmat, min_sell_price=5.0)
        db.session.add(ReactionList(user_id=user.id, eve_item_id=rprod.id, runs_count=1))
        db.session.commit()

    def test_production_route_excludes_reaction_materials(self, db, auth_client):
        client, user = auth_client
        self._seed_one_of_each(db, user)
        body = client.get(PRODUCTION_URL).data
        assert b'Tritanium' in body
        assert b'Hydrogen Iso' not in body

    def test_reaction_route_excludes_production_materials(self, db, auth_client):
        client, user = auth_client
        self._seed_one_of_each(db, user)
        body = client.get(REACTION_URL).data
        assert b'Hydrogen Iso' in body
        assert b'Tritanium' not in body


class TestComponentsToBuysDefaultStation:
    def _seed(self, db, user):
        ur = make_universe_region(db, region_id=10000098)
        uc = make_universe_constellation(db, ur, constellation_id=20000098)
        system = make_universe_system(db, uc, system_id=30000998, name='DefHub')
        hub = make_trade_hub(db, system)
        station = make_universe_station(db, system, station_id=60088888)
        mat = make_item(db, item_id=38, slug='iso-ctb', name='Isogen')
        crafted = make_item(db, item_id=39, slug='module-ctb', name='Module CTB')
        bp = make_blueprint(db, crafted, prod_qtt=5)
        bp.manufacturing_tree = {'38': {'quantity': 50, 'name': 'Isogen', 'chain': {}}}
        make_jita_min_price(db, mat, min_sell_price=10.0)
        make_production_list(db, user, crafted, hub, runs_count=1)
        make_user_asset(db, user, mat, station=station, quantity=20)
        return station

    def test_production_uses_industry_station_default(self, db, auth_client):
        client, user = auth_client
        station = self._seed(db, user)
        user.industry_modifications = {**(user.industry_modifications or {}),
                                       'current_industry_station': station.id}
        db.session.commit()

        resp = client.get(PRODUCTION_URL)   # no station_id in the query
        assert resp.status_code == 200
        assert b'In stock' in resp.data     # deduction columns shown → default applied

    def test_explicit_empty_station_id_overrides_default(self, db, auth_client):
        client, user = auth_client
        station = self._seed(db, user)
        user.industry_modifications = {**(user.industry_modifications or {}),
                                       'current_industry_station': station.id}
        db.session.commit()

        resp = client.get(f'{PRODUCTION_URL}?station_id=')   # explicit clear
        assert resp.status_code == 200
        assert b'In stock' not in resp.data

    def test_reaction_uses_reaction_station_default(self, db, auth_client):
        from evebs.models import ReactionList
        client, user = auth_client
        ur = make_universe_region(db, region_id=10000097)
        uc = make_universe_constellation(db, ur, constellation_id=20000097)
        system = make_universe_system(db, uc, system_id=30000997, name='RxnHub')
        station = make_universe_station(db, system, station_id=60077777)
        mat = make_item(db, item_id=16634, slug='hydro-def', name='Hydrogen Def')
        prod = make_item(db, item_id=16679, slug='fuller-def', name='Fullerides Def')
        bp = make_blueprint(db, prod, blueprint_id=46211, prod_qtt=3000)
        bp.activity_type = 'reaction'
        bp.manufacturing_tree = {'16634': {'quantity': 100, 'name': 'Hydrogen Def', 'chain': {}}}
        make_jita_min_price(db, mat, min_sell_price=5.0)
        db.session.add(ReactionList(user_id=user.id, eve_item_id=prod.id, runs_count=1))
        make_user_asset(db, user, mat, station=station, quantity=20)
        user.reaction_modifications = {**(user.reaction_modifications or {}),
                                       'current_reaction_station': station.id}
        db.session.commit()

        resp = client.get(REACTION_URL)
        assert resp.status_code == 200
        assert b'In stock' in resp.data


class TestComponentsToBuysStockHighlight:
    def _seed(self, db, user, stock):
        """Needs 50 Isogen for one run; `stock` units held at the station."""
        ur = make_universe_region(db, region_id=10000096)
        uc = make_universe_constellation(db, ur, constellation_id=20000096)
        system = make_universe_system(db, uc, system_id=30000996, name='HlHub')
        hub = make_trade_hub(db, system)
        station = make_universe_station(db, system, station_id=60066666)
        mat = make_item(db, item_id=38, slug='iso-hl', name='Isogen HL')
        crafted = make_item(db, item_id=39, slug='module-hl', name='Module HL')
        bp = make_blueprint(db, crafted, prod_qtt=5)
        bp.manufacturing_tree = {'38': {'quantity': 50, 'name': 'Isogen HL', 'chain': {}}}
        make_jita_min_price(db, mat, min_sell_price=10.0)
        make_production_list(db, user, crafted, hub, runs_count=1)
        make_user_asset(db, user, mat, station=station, quantity=stock)
        db.session.commit()
        return station

    def test_partial_stock_row_is_blue(self, db, auth_client):
        client, user = auth_client
        station = self._seed(db, user, stock=20)        # need 50, have 20 → partial
        resp = client.get(f'{PRODUCTION_URL}?station_id={station.id}')
        assert resp.status_code == 200
        assert b'table-info' in resp.data
        assert b'table-success' not in resp.data

    def test_full_stock_row_is_green(self, db, auth_client):
        client, user = auth_client
        station = self._seed(db, user, stock=50)        # need 50, have 50 → covered
        resp = client.get(f'{PRODUCTION_URL}?station_id={station.id}')
        assert resp.status_code == 200
        assert b'table-success' in resp.data
        assert b'table-info' not in resp.data

    def test_no_station_no_highlight(self, db, auth_client):
        client, user = auth_client
        self._seed(db, user, stock=20)
        resp = client.get(PRODUCTION_URL)               # no station selected
        assert resp.status_code == 200
        assert b'table-info' not in resp.data
        assert b'table-success' not in resp.data
