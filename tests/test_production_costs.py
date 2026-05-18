"""Tests for evebs/routes/production_costs.py show() and its Jinja2 template."""
import pytest
from datetime import datetime
from unittest.mock import patch

from evebs.extensions import db
from evebs.models import (
    UniverseCategory, UniverseGroup, UniverseType,
    Blueprint as BpModel, BlueprintMaterial,
    UniverseRegion, UniverseConstellation, UniverseSystem, UniverseStation,
    User, BpcAsset, MarketOrder, MarketPrice, Constant,
)

# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------

def _seed_cat_group(app):
    with app.app_context():
        db.session.add(UniverseCategory(id=1, name='Commodity', published=True))
        db.session.flush()
        db.session.add(UniverseGroup(id=1, name='Materials', published=True, category_id=1))
        db.session.commit()


def _seed_types(app):
    with app.app_context():
        db.session.add_all([
            UniverseType(id=165, name='Tritanium', description='', published=True,
                         group_id=1, volume=0.01),
            UniverseType(id=38,  name='Mexallon',  description='', published=True,
                         group_id=1, volume=0.5),
        ])
        db.session.commit()


def _seed_blueprint(app):
    with app.app_context():
        db.session.add(BpModel(id=681, name='Tritanium', produced_type_id=165,
                               prod_qtt=1, nb_runs=1))
        db.session.flush()
        db.session.add(BlueprintMaterial(blueprint_id=681, universe_type_id=38, required_qtt=86))
        db.session.commit()


def _seed_universe(app):
    with app.app_context():
        db.session.add(UniverseRegion(id=10000002, name='The Forge', description=''))
        db.session.flush()
        db.session.add(UniverseConstellation(id=20000020, name='Kimotoro',
                                              universe_region_id=10000002))
        db.session.flush()
        db.session.add(UniverseSystem(id=30000142, name='Jita',
                                       security_class='A', security_status=1.0,
                                       star_id=40009081,
                                       universe_constellation_id=20000020,
                                       trade_hub=True))
        db.session.commit()


def _seed_station(app):
    with app.app_context():
        db.session.add(UniverseStation(
            id=60003760, owner_id=1000035, universe_system_id=30000142,
            name='Jita IV - Moon 4 - Caldari Navy Assembly Plant',
            office_rental_cost=0.0, reprocessing_efficiency=0.5,
            reprocessing_stations_take=0.05, services=[],
        ))
        db.session.commit()


def _seed_user(app):
    with app.app_context():
        user = User(name='Pilot', provider='eve', uid='12345',
                    initialization_finalized=True)
        db.session.add(user)
        db.session.commit()
        return user.id


def _seed_asset(app, user_id, type_id=38, quantity=500, station_id=60003760):
    with app.app_context():
        db.session.add(BpcAsset(user_id=user_id, eve_item_id=type_id,
                                 quantity=quantity, universe_station_id=station_id))
        db.session.commit()


def _seed_order(app, order_id, type_id, is_buy, price, system_id=30000142):
    with app.app_context():
        db.session.add(MarketOrder(
            id=order_id, duration=90, is_buy_order=is_buy,
            issued=datetime.utcnow(), location_id=60003760, min_volume=1,
            price=price, range='station', system_id=system_id,
            type_id=type_id, volume_remain=500, volume_total=500,
            source='list_order_in_a_region',
        ))
        db.session.commit()


# ---------------------------------------------------------------------------
# Autouse cleanup — runs before conftest clean_tables (LIFO order), so FK
# references to universe_* tables are gone before conftest deletes them.
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_local_tables(app):
    yield
    with app.app_context():
        db.session.query(MarketOrder).delete()
        db.session.query(MarketPrice).delete()
        db.session.query(BpcAsset).delete()
        db.session.query(User).delete()
        db.session.query(BlueprintMaterial).delete()
        db.session.query(BpModel).delete()
        db.session.query(UniverseType).delete()
        db.session.query(UniverseGroup).delete()
        db.session.query(UniverseCategory).delete()
        db.session.query(Constant).delete()
        db.session.commit()


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_NEARBY_JITA = {'Jita': {'jumps': 0, 'security': 1.0}}


@pytest.fixture
def full_data(app):
    """Seed the minimum set: item types, blueprint, universe, station."""
    _seed_cat_group(app)
    _seed_types(app)
    _seed_blueprint(app)
    _seed_universe(app)
    _seed_station(app)


@pytest.fixture
def authed_client(app, full_data):
    """Test client logged in as a user who holds 500 Mexallon at Jita IV."""
    user_id = _seed_user(app)
    _seed_asset(app, user_id)
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user_id)
            sess['_fresh'] = True
        yield client


# ---------------------------------------------------------------------------
# Route tests
# ---------------------------------------------------------------------------

def test_404_for_missing_type(app):
    with app.test_client() as client:
        resp = client.get('/production_costs/9999')
    assert resp.status_code == 404


def test_no_blueprint_shows_warning(app):
    _seed_cat_group(app)
    _seed_types(app)
    with app.test_client() as client:
        resp = client.get('/production_costs/165')
    assert resp.status_code == 200
    assert b'No blueprint found' in resp.data


def test_materials_visible_without_login(app, full_data):
    with app.test_client() as client:
        resp = client.get('/production_costs/165')
    assert resp.status_code == 200
    assert b'Mexallon' in resp.data
    assert b'86' in resp.data  # required_qtt


def test_unauthenticated_nearby_shows_login_prompt(app, full_data):
    with app.test_client() as client:
        resp = client.get('/production_costs/165')
    assert b'Log in' in resp.data


def test_output_buyers_shown_for_buy_order(app, authed_client):
    _seed_order(app, order_id=10001, type_id=165, is_buy=True, price=98_765.0)
    with patch('evebs.engine.routing.find_systems_within_jumps', return_value=_NEARBY_JITA):
        resp = authed_client.get('/production_costs/165')
    assert resp.status_code == 200
    assert b'98' in resp.data  # ISK-formatted price fragment


def test_input_sellers_shown_for_sell_order(app, authed_client):
    _seed_order(app, order_id=20001, type_id=38, is_buy=False, price=55_000.0)
    with patch('evebs.engine.routing.find_systems_within_jumps', return_value=_NEARBY_JITA):
        resp = authed_client.get('/production_costs/165')
    assert resp.status_code == 200
    assert b'Mexallon' in resp.data
    assert b'55' in resp.data


def test_no_nearby_orders_shows_empty_states(app, authed_client):
    with patch('evebs.engine.routing.find_systems_within_jumps', return_value=_NEARBY_JITA):
        resp = authed_client.get('/production_costs/165')
    assert b'No buy orders nearby' in resp.data
    assert b'No sell orders nearby' in resp.data


def test_current_station_name_in_card_header(app, authed_client):
    with patch('evebs.engine.routing.find_systems_within_jumps', return_value=_NEARBY_JITA):
        resp = authed_client.get('/production_costs/165')
    assert b'Jita IV' in resp.data


def test_input_sellers_limited_to_3_per_material(app, authed_client):
    for i, price in enumerate([10_000.0, 20_000.0, 30_000.0, 40_000.0], start=1):
        _seed_order(app, order_id=30000 + i, type_id=38, is_buy=False, price=price)
    with patch('evebs.engine.routing.find_systems_within_jumps', return_value=_NEARBY_JITA):
        resp = authed_client.get('/production_costs/165')
    html = resp.data.decode()
    assert '10.0K' in html   # cheapest shown
    assert '30.0K' in html   # 3rd cheapest shown
    assert '40.0K' not in html  # 4th excluded


def test_only_buy_orders_for_produced_type(app, authed_client):
    """A sell order for the produced type must not appear in the buyers table."""
    _seed_order(app, order_id=40001, type_id=165, is_buy=False, price=200_000.0)
    with patch('evebs.engine.routing.find_systems_within_jumps', return_value=_NEARBY_JITA):
        resp = authed_client.get('/production_costs/165')
    assert b'No buy orders nearby' in resp.data


# ---------------------------------------------------------------------------
# Template rendering tests — render the template directly with controlled ctx
# ---------------------------------------------------------------------------

def test_template_cards_headers_present(app, full_data):
    """Buyers for output and Sellers for input headings are always rendered."""
    with app.test_client() as client:
        resp = client.get('/production_costs/165')
    assert b'Buyers for output' in resp.data
    assert b'Sellers for input' in resp.data


def test_template_summary_cards_present(app, full_data):
    with app.test_client() as client:
        resp = client.get('/production_costs/165')
    html = resp.data
    assert b'Batch size' in html
    assert b'Cost per item' in html
    assert b'Margin / item' in html


def test_template_material_icon_url(app, full_data):
    with app.test_client() as client:
        resp = client.get('/production_costs/165')
    assert b'evetech.net/types/38/icon' in resp.data


def test_template_direct_render_with_buy_order(app, full_data):
    """Render template directly with a buy order; verifies Jinja conditional for output_buyers."""
    from flask import render_template
    _seed_order(app, order_id=50001, type_id=165, is_buy=True, price=123_456.0)
    with app.test_request_context('/production_costs/165'):
        item = UniverseType.query.get(165)
        bp = BpModel.query.filter_by(produced_type_id=165).first()
        order = MarketOrder.query.get(50001)
        html = render_template(
            'production_costs/show.html',
            item=item, blueprint=bp, market_prices={}, owned_quantities={},
            taxes=1.13, current_station=None,
            output_buyers=[order], input_sellers={}, title='test',
        )
    assert 'Buyers for output' in html
    assert '123' in html           # price fragment
    assert 'Jita' in html          # system name via order.universe_system


def test_template_direct_render_with_sell_order(app, full_data):
    """Render template directly with a sell order; verifies grouped seller rows."""
    from flask import render_template
    _seed_order(app, order_id=60001, type_id=38, is_buy=False, price=77_000.0)
    with app.test_request_context('/production_costs/165'):
        item = UniverseType.query.get(165)
        bp = BpModel.query.filter_by(produced_type_id=165).first()
        order = MarketOrder.query.get(60001)
        html = render_template(
            'production_costs/show.html',
            item=item, blueprint=bp, market_prices={}, owned_quantities={},
            taxes=1.13, current_station=None,
            output_buyers=[], input_sellers={38: [order]}, title='test',
        )
    assert 'Sellers for input' in html
    assert 'Mexallon' in html
    assert '77.0K' in html


def test_template_direct_render_station_in_header(app, full_data):
    """current_station name appears in the card sub-header when provided."""
    from flask import render_template
    with app.test_request_context('/production_costs/165'):
        item = UniverseType.query.get(165)
        bp = BpModel.query.filter_by(produced_type_id=165).first()
        station = UniverseStation.query.get(60003760)
        html = render_template(
            'production_costs/show.html',
            item=item, blueprint=bp, market_prices={}, owned_quantities={},
            taxes=1.13, current_station=station,
            output_buyers=[], input_sellers={}, title='test',
        )
    assert 'Jita IV' in html
    assert 'No buy orders nearby' in html
    assert 'No sell orders nearby' in html
