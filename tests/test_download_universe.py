"""Tests for esi/download_universe.py.

ESI HTTP calls are mocked via unittest.mock.patch on esi.client.requests.get.
All DB assertions run against a real PostgreSQL test database (evebs_test).
"""
from unittest.mock import patch, MagicMock

import pytest

from evebs.extensions import db
from evebs.models import UniverseRegion, UniverseConstellation, UniverseSystem, UniverseStation
from esi.download_universe import download_universe


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

def _resp(data):
    r = MagicMock()
    r.ok = True
    r.status_code = 200
    r.headers = {'x-pages': '1', 'X-Ratelimit-Remaining': '100'}
    r.json.return_value = data
    return r


_BASE = 'https://esi.evetech.net/latest/'

_STATION_DATA = {
    'name': 'Jita IV - Moon 4 - Caldari Navy Assembly Plant',
    'office_rental_cost': 10000.0,
    'security_status': 0.9459,
    'owner': 1000035,
    'reprocessing_efficiency': 0.5,
    'reprocessing_stations_take': 0.025,
    'services': ['market', 'repair-facilities'],
}

_FULL_RESPONSES = {
    f'{_BASE}universe/regions/':              [10000001],
    f'{_BASE}universe/regions/10000001/':     {'name': 'The Forge', 'description': 'A region.', 'constellations': [20000001]},
    f'{_BASE}universe/constellations/20000001/': {'name': 'Kimotoro', 'systems': [30000142]},
    f'{_BASE}universe/systems/30000142/':     {
        'name': 'Jita', 'security_status': 0.9459, 'security_class': 'B',
        'star_id': 40009081, 'stations': [60003760],
    },
    f'{_BASE}universe/stations/60003760/': _STATION_DATA,
}


def _make_side_effect(responses):
    def side_effect(url, params=None, timeout=30):
        # Strip query params from URL for matching
        bare_url = url.split('?')[0]
        if bare_url not in responses:
            raise ValueError(f'Unmocked ESI URL: {bare_url}')
        return _resp(responses[bare_url])
    return side_effect


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_inserts_full_hierarchy(app):
    with app.app_context():
        with patch('esi.client.requests.get', side_effect=_make_side_effect(_FULL_RESPONSES)):
            download_universe()

        region = UniverseRegion.query.filter_by(cpp_region_id=10000001).first()
        assert region is not None
        assert region.name == 'The Forge'
        assert region.description == 'A region.'

        constellation = UniverseConstellation.query.filter_by(cpp_constellation_id=20000001).first()
        assert constellation is not None
        assert constellation.name == 'Kimotoro'
        assert constellation.universe_region_id == region.id

        system = UniverseSystem.query.filter_by(cpp_system_id=30000142).first()
        assert system is not None
        assert system.name == 'Jita'
        assert abs(system.security_status - 0.9459) < 1e-4
        assert system.universe_constellation_id == constellation.id

        station = UniverseStation.query.filter_by(cpp_station_id=60003760).first()
        assert station is not None
        assert station.name == 'Jita IV - Moon 4 - Caldari Navy Assembly Plant'
        assert station.universe_system_id == system.id
        assert station.services == ['market', 'repair-facilities']


def test_updates_existing_records(app):
    updated_responses = dict(_FULL_RESPONSES)
    updated_responses[f'{_BASE}universe/regions/10000001/'] = {
        'name': 'The Forge Updated', 'description': 'New desc.', 'constellations': [20000001],
    }
    updated_responses[f'{_BASE}universe/stations/60003760/'] = {
        **_STATION_DATA,
        'name': 'Jita Station Renamed',
        'office_rental_cost': 99999.0,
    }

    with app.app_context():
        with patch('esi.client.requests.get', side_effect=_make_side_effect(_FULL_RESPONSES)):
            download_universe()
        with patch('esi.client.requests.get', side_effect=_make_side_effect(updated_responses)):
            download_universe()

        assert UniverseRegion.query.count() == 1
        assert UniverseConstellation.query.count() == 1
        assert UniverseSystem.query.count() == 1
        assert UniverseStation.query.count() == 1

        region = UniverseRegion.query.filter_by(cpp_region_id=10000001).first()
        assert region.name == 'The Forge Updated'
        assert region.description == 'New desc.'

        station = UniverseStation.query.filter_by(cpp_station_id=60003760).first()
        assert station.name == 'Jita Station Renamed'
        assert station.office_rental_cost == 99999.0


def test_skips_region_with_no_detail(app):
    responses = {
        f'{_BASE}universe/regions/':          [10000001],
        f'{_BASE}universe/regions/10000001/': None,
    }

    def side_effect(url, params=None, timeout=30):
        bare_url = url.split('?')[0]
        data = responses.get(bare_url)
        if data is None and bare_url in responses:
            # Simulate ESI returning empty/falsy — client returns the value as-is
            r = MagicMock()
            r.ok = True
            r.status_code = 200
            r.headers = {'x-pages': '1', 'X-Ratelimit-Remaining': '100'}
            r.json.return_value = {}
            return r
        if bare_url not in responses:
            raise ValueError(f'Unmocked ESI URL: {bare_url}')
        return _resp(data)

    with app.app_context():
        with patch('esi.client.requests.get', side_effect=side_effect):
            download_universe()

        assert UniverseRegion.query.count() == 0


def test_region_with_no_constellations(app):
    responses = {
        f'{_BASE}universe/regions/':          [10000001],
        f'{_BASE}universe/regions/10000001/': {'name': 'Empty Region', 'description': '', 'constellations': []},
    }

    with app.app_context():
        with patch('esi.client.requests.get', side_effect=_make_side_effect(responses)):
            download_universe()

        assert UniverseRegion.query.count() == 1
        assert UniverseConstellation.query.count() == 0
        assert UniverseSystem.query.count() == 0
        assert UniverseStation.query.count() == 0


def test_new_system_trade_hub_defaults_to_false(app):
    # trade_hub is nullable=False in the DB; download_universe must set it
    # explicitly so inserts don't raise a NOT NULL violation.
    with app.app_context():
        with patch('esi.client.requests.get', side_effect=_make_side_effect(_FULL_RESPONSES)):
            download_universe()

        system = UniverseSystem.query.filter_by(cpp_system_id=30000142).first()
        assert system is not None
        assert system.trade_hub is False


def test_system_with_no_stations(app):
    responses = dict(_FULL_RESPONSES)
    responses[f'{_BASE}universe/systems/30000142/'] = {
        'name': 'Jita', 'security_status': 0.9459, 'security_class': 'B',
        'star_id': 40009081, 'stations': [],
    }

    with app.app_context():
        with patch('esi.client.requests.get', side_effect=_make_side_effect(responses)):
            download_universe()

        assert UniverseSystem.query.filter_by(cpp_system_id=30000142).first() is not None
        assert UniverseStation.query.count() == 0


def test_multiple_regions(app):
    responses = {
        f'{_BASE}universe/regions/':          [10000001, 10000002],
        f'{_BASE}universe/regions/10000001/': {'name': 'The Forge', 'description': '', 'constellations': []},
        f'{_BASE}universe/regions/10000002/': {'name': 'Domain', 'description': '', 'constellations': []},
    }

    with app.app_context():
        with patch('esi.client.requests.get', side_effect=_make_side_effect(responses)):
            download_universe()

        assert UniverseRegion.query.count() == 2
        names = {r.name for r in UniverseRegion.query.all()}
        assert names == {'The Forge', 'Domain'}
