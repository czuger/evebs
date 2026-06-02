"""Tests for DownloadMyAssets.update — ESI HTTP mocked, real DB."""
import pytest
from datetime import datetime
from unittest.mock import patch

from esi.download_my_assets import DownloadMyAssets, STRUCTURE_ID_MIN, _resolve_root_location
from tests.factories import (
    make_universe_region, make_universe_constellation,
    make_universe_system, make_universe_station, make_universe_structure,
    make_item, make_bpc_asset,
)

STRUCTURE_ID = STRUCTURE_ID_MIN + 1


@pytest.fixture
def seeded(db):
    ur = make_universe_region(db)
    uc = make_universe_constellation(db, ur)
    us = make_universe_system(db, uc)
    station = make_universe_station(db, us, station_id=60003760)
    item = make_item(db, item_id=34, slug='tritanium')
    db.session.commit()
    return {'system': us, 'station': station, 'item': item}


def _esi_asset(type_id=34, location_id=60003760, quantity=5, item_id=1,
               location_flag='Hangar', location_type='station'):
    return {
        'item_id': item_id,
        'type_id': type_id,
        'location_id': location_id,
        'quantity': quantity,
        'location_flag': location_flag,
        'location_type': location_type,
    }


def _esi_structure_asset(type_id=34, quantity=5):
    return {
        'item_id': 2,
        'type_id': type_id,
        'location_id': STRUCTURE_ID,
        'quantity': quantity,
        'location_flag': 'Hangar',
        'location_type': 'item',
    }



class TestDownloadMyAssets:
    def test_creates_bpc_asset(self, db, user, seeded):
        with patch('esi.client.EsiClient.get_all_pages', return_value=[_esi_asset()]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True):
            DownloadMyAssets().update(user)

        from evebs.models import BpcAsset
        assets = BpcAsset.query.filter_by(user_id=user.id).all()
        assert len(assets) == 1
        assert assets[0].quantity == 5
        assert assets[0].eve_item_id == seeded['item'].id
        assert assets[0].universe_station_id == seeded['station'].id
        assert assets[0].location_flag == 'Hangar'
        assert assets[0].location_type == 'station'

    def test_updates_quantity_on_existing_asset(self, db, user, seeded):
        existing = make_bpc_asset(db, user, seeded['item'], quantity=3)
        db.session.commit()

        with patch('esi.client.EsiClient.get_all_pages', return_value=[_esi_asset(quantity=10)]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True):
            DownloadMyAssets().update(user)

        db.session.expire(existing)
        assert existing.quantity == 10
        assert existing.touched is True

    def test_deletes_assets_not_in_esi_response(self, db, user, seeded):
        stale = make_bpc_asset(db, user, seeded['item'], quantity=7)
        db.session.commit()

        item2 = make_item(db, item_id=35, slug='pyerite')
        db.session.commit()

        with patch('esi.client.EsiClient.get_all_pages',
                   return_value=[_esi_asset(type_id=35)]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True):
            DownloadMyAssets().update(user)

        from evebs.models import BpcAsset
        ids = [a.eve_item_id for a in BpcAsset.query.filter_by(user_id=user.id).all()]
        assert seeded['item'].id not in ids
        assert item2.id in ids

    def test_skips_locked_user(self, db, user, seeded):
        user.locked = True
        db.session.commit()

        with patch('esi.client.EsiClient.get_all_pages') as mock_pages:
            DownloadMyAssets().update(user)
            mock_pages.assert_not_called()

    def test_skips_unknown_item_type(self, db, user, seeded):
        with patch('esi.client.EsiClient.get_all_pages',
                   return_value=[_esi_asset(type_id=99999)]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True):
            DownloadMyAssets().update(user)

        from evebs.models import BpcAsset
        assert BpcAsset.query.filter_by(user_id=user.id).count() == 0

    def test_updates_download_flags(self, db, user, seeded):
        before = datetime.utcnow()
        with patch('esi.client.EsiClient.get_all_pages', return_value=[_esi_asset()]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True):
            DownloadMyAssets().update(user)

        db.session.expire(user)
        assert user.download_assets_running is False
        assert user.last_assets_download >= before


class TestDownloadMyAssetsStructure:
    def test_stores_structure_id_when_known(self, db, user, seeded):
        make_universe_structure(db, seeded['system'], structure_id=STRUCTURE_ID)
        db.session.commit()

        with patch('esi.client.EsiClient.get_all_pages', return_value=[_esi_structure_asset()]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True):
            DownloadMyAssets().update(user)

        from evebs.models import BpcAsset
        assets = BpcAsset.query.filter_by(user_id=user.id).all()
        assert len(assets) == 1
        assert assets[0].universe_structure_id == STRUCTURE_ID
        assert assets[0].universe_station_id is None

    def test_stores_raw_structure_id_when_unknown(self, db, user, seeded):
        import re
        with patch('esi.client.EsiClient.get_all_pages', return_value=[_esi_structure_asset()]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True):
            DownloadMyAssets().update(user)

        from evebs.models import BpcAsset, UniverseStructure, UnknownStructure
        assert db.session.get(UniverseStructure, STRUCTURE_ID) is None
        unknown = db.session.get(UnknownStructure, STRUCTURE_ID)
        assert unknown is not None
        assert re.match(r'^[A-Z]{2}-\d{3}$', unknown.name)
        assets = BpcAsset.query.filter_by(user_id=user.id).all()
        assert len(assets) == 1
        assert assets[0].universe_structure_id == STRUCTURE_ID

    def test_reuses_existing_unknown_structure(self, db, user, seeded):
        item2 = make_item(db, item_id=35, slug='pyerite')
        db.session.commit()

        with patch('esi.client.EsiClient.get_all_pages', return_value=[_esi_structure_asset()]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True):
            DownloadMyAssets().update(user)

        with patch('esi.client.EsiClient.get_all_pages',
                   return_value=[_esi_structure_asset(type_id=35)]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True):
            DownloadMyAssets().update(user)

        from evebs.models import UnknownStructure
        assert UnknownStructure.query.filter_by(id=STRUCTURE_ID).count() == 1


class TestResolveRootLocation:
    def test_direct_station_asset(self):
        asset = {'item_id': 1, 'type_id': 34, 'location_id': 60003760, 'location_type': 'station'}
        assert _resolve_root_location(asset, {1: asset}) is asset

    def test_asset_in_container_at_station(self):
        container = {'item_id': 10, 'location_id': 60003760, 'location_type': 'station'}
        item = {'item_id': 20, 'location_id': 10, 'location_type': 'item'}
        index = {10: container, 20: item}
        result = _resolve_root_location(item, index)
        assert result is container
        assert result['location_id'] == 60003760

    def test_nested_containers(self):
        station_asset = {'item_id': 10, 'location_id': 60003760, 'location_type': 'station'}
        outer_can  = {'item_id': 20, 'location_id': 10, 'location_type': 'item'}
        inner_can  = {'item_id': 30, 'location_id': 20, 'location_type': 'item'}
        deep_item  = {'item_id': 40, 'location_id': 30, 'location_type': 'item'}
        index = {10: station_asset, 20: outer_can, 30: inner_can, 40: deep_item}
        result = _resolve_root_location(deep_item, index)
        assert result is station_asset

    def test_asset_in_structure(self):
        structure = {'item_id': 10, 'location_id': STRUCTURE_ID, 'location_type': 'item'}
        item = {'item_id': 20, 'location_id': 10, 'location_type': 'item'}
        index = {10: structure, 20: item}
        result = _resolve_root_location(item, index)
        assert result is structure

    def test_orphaned_container_stops_gracefully(self):
        item = {'item_id': 20, 'location_id': 99999, 'location_type': 'item'}
        index = {20: item}
        result = _resolve_root_location(item, index)
        assert result is item

    def test_integration_container_at_station(self, db, user, seeded):
        container_id = 9_000_000_001
        pages = [
            {'item_id': container_id, 'type_id': 17366,
             'location_id': seeded['station'].id, 'location_type': 'station',
             'location_flag': 'Hangar', 'quantity': 1},
            {'item_id': 9_000_000_002, 'type_id': 34,
             'location_id': container_id, 'location_type': 'item',
             'location_flag': 'Cargo', 'quantity': 5},
        ]
        with patch('esi.client.EsiClient.get_all_pages', return_value=pages), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True):
            DownloadMyAssets().update(user)

        from evebs.models import BpcAsset
        assets = BpcAsset.query.filter_by(user_id=user.id).all()
        eve_ids = {a.universe_station_id for a in assets}
        assert seeded['station'].id in eve_ids
