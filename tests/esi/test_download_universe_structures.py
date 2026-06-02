"""Tests for DownloadUniverseStructures — EveRef bulk dataset mocked, real DB."""
from unittest.mock import patch

from esi.download_universe_structures import DownloadUniverseStructures
from tests.factories import (
    make_universe_region, make_universe_constellation, make_universe_system,
)


def _mock_response(data: dict):
    mock_resp = __import__('unittest.mock', fromlist=['MagicMock']).MagicMock()
    mock_resp.json.return_value = data
    mock_resp.raise_for_status.return_value = None
    return mock_resp


def _structure_record(structure_id=1021011818054, name='Jita Trade Hub',
                      owner_id=507020344, type_id=35832, solar_system_id=30000142):
    return {
        str(structure_id): {
            'structure_id': structure_id,
            'name': name,
            'owner_id': owner_id,
            'type_id': type_id,
            'solar_system_id': solar_system_id,
            'is_public_structure': True,
        }
    }


class TestDownloadUniverseStructures:
    def test_creates_new_structure(self, db):
        ur = make_universe_region(db)
        uc = make_universe_constellation(db, ur)
        make_universe_system(db, uc, system_id=30000142)
        db.session.commit()

        with patch('requests.get', return_value=_mock_response(_structure_record())):
            DownloadUniverseStructures().download()

        from evebs.models import UniverseStructure
        s = db.session.get(UniverseStructure, 1021011818054)
        assert s is not None
        assert s.name == 'Jita Trade Hub'
        assert s.owner_id == 507020344
        assert s.type_id == 35832
        assert s.universe_system_id == 30000142

    def test_updates_existing_structure(self, db):
        from evebs.models import UniverseStructure
        ur = make_universe_region(db)
        uc = make_universe_constellation(db, ur)
        make_universe_system(db, uc, system_id=30000142)
        existing = UniverseStructure(id=1021011818054, name='Old Name',
                                     owner_id=1, type_id=35832)
        db.session.add(existing)
        db.session.commit()

        with patch('requests.get', return_value=_mock_response(_structure_record(name='New Name'))):
            DownloadUniverseStructures().download()

        db.session.expire(existing)
        assert existing.name == 'New Name'
        assert existing.owner_id == 507020344
        assert existing.universe_system_id == 30000142

    def test_skips_record_without_owner_id(self, db):
        data = {'1021011818054': {'structure_id': 1021011818054, 'name': 'Ghost',
                                  'solar_system_id': 30000142}}
        with patch('requests.get', return_value=_mock_response(data)):
            DownloadUniverseStructures().download()

        from evebs.models import UniverseStructure
        assert UniverseStructure.query.count() == 0

    def test_uses_dict_key_when_structure_id_field_absent(self, db):
        data = {'1021011818054': {'name': 'No ID Field', 'owner_id': 99,
                                  'type_id': 35832, 'solar_system_id': 30000142}}
        with patch('requests.get', return_value=_mock_response(data)):
            DownloadUniverseStructures().download()

        from evebs.models import UniverseStructure
        s = db.session.get(UniverseStructure, 1021011818054)
        assert s is not None
        assert s.name == 'No ID Field'

    def test_unknown_solar_system_stores_null_fk(self, db):
        data = _structure_record(solar_system_id=99999999)
        with patch('requests.get', return_value=_mock_response(data)):
            DownloadUniverseStructures().download()

        from evebs.models import UniverseStructure
        s = db.session.get(UniverseStructure, 1021011818054)
        assert s is not None
        assert s.universe_system_id is None

    def test_handles_multiple_structures(self, db):
        data = {
            **_structure_record(structure_id=1000000000001, name='Alpha'),
            **_structure_record(structure_id=1000000000002, name='Beta'),
        }
        with patch('requests.get', return_value=_mock_response(data)):
            DownloadUniverseStructures().download()

        from evebs.models import UniverseStructure
        assert UniverseStructure.query.count() == 2
