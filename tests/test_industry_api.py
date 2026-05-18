"""Tests for GET /api/industry/facilities/near/."""
import pytest
from unittest.mock import patch

from evebs.extensions import db
from evebs.models import (
    UniverseRegion, UniverseConstellation, UniverseSystem, UniverseStation,
    User, IndustryFacility,
)

_NEARBY_JITA = {'Jita': {'jumps': 0, 'security': 1.0}}


# ---------------------------------------------------------------------------
# Cleanup — runs before conftest clean_tables (LIFO), keeping FK order
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_local(app):
    yield
    with app.app_context():
        db.session.query(IndustryFacility).delete()
        db.session.query(User).delete()
        db.session.commit()


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def universe(app):
    with app.app_context():
        db.session.add(UniverseRegion(id=10000002, name='The Forge', description=''))
        db.session.flush()
        db.session.add(UniverseConstellation(id=20000020, name='Kimotoro',
                                              universe_region_id=10000002))
        db.session.flush()
        db.session.add(UniverseSystem(
            id=30000142, name='Jita', security_class='A', security_status=1.0,
            star_id=40009081, universe_constellation_id=20000020, trade_hub=True,
            cost_indices=[{'activity': 'manufacturing', 'cost_index': 0.04}],
        ))
        db.session.flush()
        db.session.add(UniverseStation(
            id=60003760, owner_id=1000035, universe_system_id=30000142,
            name='Jita IV - Moon 4 - Caldari Navy Assembly Plant',
            office_rental_cost=0.0, reprocessing_efficiency=0.5,
            reprocessing_stations_take=0.05, services=[],
        ))
        db.session.commit()


def _seed_user(app, station_id=None):
    with app.app_context():
        user = User(name='Pilot', provider='eve', uid='12345',
                    initialization_finalized=True,
                    user_location_station_id=station_id,
                    max_jumps=5, avoid_low_sec=False, avoid_null_sec=False)
        db.session.add(user)
        db.session.commit()
        return user.id


def _seed_facility(app):
    with app.app_context():
        db.session.add(IndustryFacility(
            id=1234567890, universe_system_id=30000142,
            universe_station_id=60003760, owner_id=1000035,
            type_id=35825, tax=0.025,
        ))
        db.session.commit()


def _login(client, user_id):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user_id)
        sess['_fresh'] = True


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_api_returns_400_when_no_location(app):
    user_id = _seed_user(app, station_id=None)
    with app.test_client() as client:
        _login(client, user_id)
        resp = client.get('/api/industry/facilities/near/')
    assert resp.status_code == 400
    assert b'No location' in resp.data


def test_api_returns_200_with_valid_location(app, universe):
    user_id = _seed_user(app, station_id=60003760)
    _seed_facility(app)
    with app.test_client() as client:
        _login(client, user_id)
        with patch('evebs.engine.industry.find_systems_within_jumps',
                   return_value=_NEARBY_JITA):
            resp = client.get('/api/industry/facilities/near/')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    row = data[0]
    assert row['system_name'] == 'Jita'
    assert row['jumps'] == 0
    assert abs(row['cost_index'] - 0.04) < 1e-9
    assert abs(row['tax'] - 0.025) < 1e-9
    assert abs(row['total_cost'] - 0.065) < 1e-9


def test_api_returns_empty_list_when_no_facilities(app, universe):
    user_id = _seed_user(app, station_id=60003760)
    with app.test_client() as client:
        _login(client, user_id)
        with patch('evebs.engine.industry.find_systems_within_jumps',
                   return_value=_NEARBY_JITA):
            resp = client.get('/api/industry/facilities/near/')
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_api_sorted_by_total_cost(app, universe):
    """Facilities are returned cheapest first."""
    user_id = _seed_user(app, station_id=60003760)
    with app.app_context():
        db.session.add_all([
            IndustryFacility(id=111, universe_system_id=30000142,
                             owner_id=1, type_id=1, tax=0.10),
            IndustryFacility(id=222, universe_system_id=30000142,
                             owner_id=1, type_id=1, tax=0.01),
        ])
        db.session.commit()
    with app.test_client() as client:
        _login(client, user_id)
        with patch('evebs.engine.industry.find_systems_within_jumps',
                   return_value=_NEARBY_JITA):
            resp = client.get('/api/industry/facilities/near/')
    data = resp.get_json()
    assert data[0]['total_cost'] <= data[1]['total_cost']
    assert data[0]['facility_id'] == 222
