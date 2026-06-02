"""Tests for evebs/routes/my_assets.py."""


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
        from tests.factories import (
            make_universe_region, make_universe_constellation,
            make_universe_system, make_universe_station,
        )
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
