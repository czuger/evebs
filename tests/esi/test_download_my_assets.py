"""Tests for DownloadMyAssets.update — ESI HTTP mocked, real DB."""
import pytest
from datetime import datetime
from unittest.mock import patch

from esi.download_my_assets import DownloadMyAssets
from tests.factories import (
    make_universe_region, make_universe_constellation,
    make_universe_system, make_universe_station,
    make_item, make_bpc_asset,
)


@pytest.fixture
def seeded(db):
    ur = make_universe_region(db)
    uc = make_universe_constellation(db, ur)
    us = make_universe_system(db, uc)
    station = make_universe_station(db, us, cpp_station_id=60003760)
    item = make_item(db, cpp_eve_item_id=34, slug='tritanium')
    db.session.commit()
    return {'station': station, 'item': item}


def _esi_asset(type_id=34, location_id=60003760, quantity=5, item_id=1):
    return {
        'item_id': item_id,
        'type_id': type_id,
        'location_id': location_id,
        'quantity': quantity,
        'location_type': 'station',
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

        item2 = make_item(db, cpp_eve_item_id=35, slug='pyerite')
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
