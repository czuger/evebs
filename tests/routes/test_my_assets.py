"""Tests for evebs/routes/my_assets.py."""
from tests.factories import (
    make_universe_region, make_universe_constellation,
    make_universe_system, make_universe_station, make_item, make_bpc_asset,
)


class TestMyAssetsShow:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/my_assets')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        resp = client.get('/my_assets')
        assert resp.status_code == 200

    def test_empty_assets_renders(self, auth_client):
        client, _ = auth_client
        resp = client.get('/my_assets')
        assert b'No assets.' in resp.data


class TestSetAssetsStation:
    def test_redirects_unauthenticated(self, client):
        resp = client.post('/my_assets/set_assets_station', data={'station_id': '1'})
        assert resp.status_code == 302

    def test_sets_station_and_redirects(self, db, auth_client):
        ur = make_universe_region(db, region_id=10000099)
        uc = make_universe_constellation(db, ur, constellation_id=20000099)
        us = make_universe_system(db, uc, system_id=30000999, name='TestSys')
        st = make_universe_station(db, us, station_id=60009999)
        db.session.commit()
        client, user = auth_client
        resp = client.post('/my_assets/set_assets_station', data={'station_id': str(st.id)})
        assert resp.status_code == 302
        db.session.refresh(user)
        assert user.selected_assets_station_id == st.id


class TestMyAssetsFilter:
    def _setup(self, db, auth_client):
        ur = make_universe_region(db, region_id=10000002)
        uc = make_universe_constellation(db, ur)
        us = make_universe_system(db, uc, system_id=30000142)
        st1 = make_universe_station(db, us, station_id=60003760)
        st2 = make_universe_station(db, us, station_id=60003761)
        item1 = make_item(db, item_id=34, slug='tritanium', name='Tritanium')
        item2 = make_item(db, item_id=35, slug='pyerite', name='Pyerite')
        _, user = auth_client
        make_bpc_asset(db, user, item1, station=st1)
        make_bpc_asset(db, user, item2, station=st2)
        db.session.commit()
        return st1, st2, item1, item2

    def test_no_filter_shows_all(self, db, auth_client):
        self._setup(db, auth_client)
        client, _ = auth_client
        resp = client.get('/my_assets')
        assert b'Tritanium' in resp.data
        assert b'Pyerite' in resp.data

    def test_filter_by_station_shows_only_that_station(self, db, auth_client):
        st1, st2, item1, item2 = self._setup(db, auth_client)
        client, _ = auth_client
        resp = client.get(f'/my_assets?location_id={st1.id}')
        assert b'Tritanium' in resp.data
        assert b'Pyerite' not in resp.data

    def test_filter_by_structure_shows_only_that_structure(self, db, auth_client):
        from evebs.models import UnknownStructure
        ur = make_universe_region(db, region_id=10000003)
        uc = make_universe_constellation(db, ur, constellation_id=20000021)
        us = make_universe_system(db, uc, system_id=30000143)
        item1 = make_item(db, item_id=36, slug='mexallon', name='Mexallon')
        item2 = make_item(db, item_id=37, slug='isogen', name='Isogen')
        _, user = auth_client
        STRUCT_A, STRUCT_B = 1_000_000_000_001, 1_000_000_000_002
        unknown_a = UnknownStructure(id=STRUCT_A, name='AA-001')
        unknown_b = UnknownStructure(id=STRUCT_B, name='BB-002')
        db.session.add_all([unknown_a, unknown_b])
        from evebs.models import BpcAsset
        db.session.add(BpcAsset(user_id=user.id, eve_item_id=item1.id,
                                universe_structure_id=STRUCT_A, quantity=1, touched=True))
        db.session.add(BpcAsset(user_id=user.id, eve_item_id=item2.id,
                                universe_structure_id=STRUCT_B, quantity=1, touched=True))
        db.session.commit()
        client, _ = auth_client
        resp = client.get(f'/my_assets?location_id={STRUCT_A}')
        assert b'Mexallon' in resp.data
        assert b'Isogen' not in resp.data
