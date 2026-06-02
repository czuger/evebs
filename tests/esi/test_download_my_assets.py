"""Tests for DownloadMyAssets.update — ESI HTTP mocked, real DB."""
import pytest
from datetime import datetime
from unittest.mock import patch

from esi.download_my_assets import DownloadMyAssets, STRUCTURE_ID_MIN
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


def _esi_asset(type_id=34, location_id=60003760, quantity=5, item_id=1):
    return {
        'item_id': item_id,
        'type_id': type_id,
        'location_id': location_id,
        'quantity': quantity,
        'location_type': 'station',
    }


def _esi_structure_asset(type_id=34, quantity=5):
    return {
        'item_id': 2,
        'type_id': type_id,
        'location_id': STRUCTURE_ID,
        'quantity': quantity,
        'location_type': 'item',
    }


def _esi_structure_data(system_id=30000142):
    return {
        'name': 'Jita Trade Hub Alpha',
        'owner_id': 98790350,
        'solar_system_id': system_id,
        'type_id': 35835,
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
    def test_creates_structure_and_bpc_asset(self, db, user, seeded):
        system = seeded['system']
        with patch('esi.client.EsiClient.get_all_pages', return_value=[_esi_structure_asset()]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True), \
             patch('esi.client.EsiClient.get_page', return_value=_esi_structure_data(system_id=system.id)):
            DownloadMyAssets().update(user)

        from evebs.models import BpcAsset, UniverseStructure
        structure = db.session.get(UniverseStructure, STRUCTURE_ID)
        assert structure is not None
        assert structure.name == 'Jita Trade Hub Alpha'
        assert structure.owner_id == 98790350
        assert structure.universe_system_id == system.id

        assets = BpcAsset.query.filter_by(user_id=user.id).all()
        assert len(assets) == 1
        assert assets[0].universe_structure_id == structure.id
        assert assets[0].universe_station_id is None

    def test_reuses_existing_structure_without_esi_call(self, db, user, seeded):
        existing = make_universe_structure(db, seeded['system'], structure_id=STRUCTURE_ID)
        db.session.commit()

        with patch('esi.client.EsiClient.get_all_pages', return_value=[_esi_structure_asset()]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True), \
             patch('esi.client.EsiClient.get_page') as mock_get_page:
            DownloadMyAssets().update(user)
            mock_get_page.assert_not_called()

        from evebs.models import BpcAsset
        assets = BpcAsset.query.filter_by(user_id=user.id).all()
        assert len(assets) == 1
        assert assets[0].universe_structure_id == existing.id

    def test_unknown_solar_system_stores_null_fk(self, db, user, seeded):
        with patch('esi.client.EsiClient.get_all_pages', return_value=[_esi_structure_asset()]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True), \
             patch('esi.client.EsiClient.get_page', return_value=_esi_structure_data(system_id=99999999)):
            DownloadMyAssets().update(user)

        from evebs.models import UniverseStructure
        structure = db.session.get(UniverseStructure, STRUCTURE_ID)
        assert structure is not None
        assert structure.universe_system_id is None

    def test_structure_auth_failure_creates_asset_without_structure_link(self, db, user, seeded):
        with patch('esi.client.EsiClient.get_all_pages', return_value=[_esi_structure_asset()]), \
             patch('esi.client.EsiClient.set_auth_token', side_effect=[True, False]):
            DownloadMyAssets().update(user)

        from evebs.models import BpcAsset, UniverseStructure
        assert db.session.get(UniverseStructure, STRUCTURE_ID) is None
        assets = BpcAsset.query.filter_by(user_id=user.id).all()
        assert len(assets) == 1
        assert assets[0].universe_structure_id is None
