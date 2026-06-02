"""Tests for DownloadUniverseStations — ESI HTTP mocked, real DB."""
from unittest.mock import patch, MagicMock

from esi.download_universe_stations import DownloadUniverseStations
from tests.factories import (
    make_universe_region, make_universe_constellation, make_universe_system,
    make_universe_station,
)


def _mock_esi(station_data):
    mock = MagicMock()
    mock.ok = True
    mock.headers = {'x-pages': '1'}
    mock.json.return_value = station_data
    return mock


def _station_data(station_id=60003760, name='Jita IV - Moon 4 - Caldari Navy Assembly Plant',
                  office_rental_cost=10000.0, security=0.946):
    return {
        'station_id': station_id,
        'name': name,
        'office_rental_cost': office_rental_cost,
        'system_security_status': security,
        'solar_system_id': 30000142,
    }


class TestDownloadUniverseStations:
    def test_fills_empty_station_name(self, db):
        ur = make_universe_region(db)
        uc = make_universe_constellation(db, ur)
        us = make_universe_system(db, uc, system_id=30000142)
        st = make_universe_station(db, us, station_id=60003760)
        st.name = ''
        db.session.commit()

        with patch('esi.client.requests.get', return_value=_mock_esi(_station_data())):
            DownloadUniverseStations().download()

        db.session.expire(st)
        assert st.name == 'Jita IV - Moon 4 - Caldari Navy Assembly Plant'
        assert st.office_rental_cost == 10000.0
        assert st.security_status == 0.946

    def test_skips_station_with_existing_name_by_default(self, db):
        ur = make_universe_region(db)
        uc = make_universe_constellation(db, ur)
        us = make_universe_system(db, uc)
        st = make_universe_station(db, us, station_id=60003760)
        st.name = 'Already Named'
        db.session.commit()

        with patch('esi.client.requests.get') as mock_get:
            DownloadUniverseStations().download(empty_only=True)
            mock_get.assert_not_called()

        db.session.expire(st)
        assert st.name == 'Already Named'

    def test_updates_all_when_empty_only_false(self, db):
        ur = make_universe_region(db)
        uc = make_universe_constellation(db, ur)
        us = make_universe_system(db, uc, system_id=30000142)
        st = make_universe_station(db, us, station_id=60003760)
        st.name = 'Old Name'
        db.session.commit()

        with patch('esi.client.requests.get', return_value=_mock_esi(_station_data())):
            DownloadUniverseStations().download(empty_only=False)

        db.session.expire(st)
        assert st.name == 'Jita IV - Moon 4 - Caldari Navy Assembly Plant'

    def test_handles_esi_not_found(self, db):
        from esi.errors import NotFound
        ur = make_universe_region(db)
        uc = make_universe_constellation(db, ur)
        us = make_universe_system(db, uc)
        st = make_universe_station(db, us, station_id=60003760)
        st.name = ''
        db.session.commit()

        with patch('esi.client.requests.get') as mock_get:
            mock_get.return_value.ok = False
            mock_get.return_value.status_code = 404
            mock_get.return_value.text = 'Not Found'
            mock_get.return_value.headers = {'x-pages': '1'}
            DownloadUniverseStations().download()

        db.session.expire(st)
        assert st.name == ''
