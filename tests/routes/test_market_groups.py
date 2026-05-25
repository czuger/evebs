"""Tests for evebs/routes/market_groups.py."""
from tests.factories import make_market_group


class TestMarketGroupsIndex:
    def test_returns_200_unauthenticated(self, client, db):
        resp = client.get('/market_groups')
        assert resp.status_code == 200

    def test_shows_root_groups(self, client, db):
        make_market_group(db, cpp_market_group_id=1, name='Ammunition & Charges')
        db.session.commit()
        resp = client.get('/market_groups')
        assert resp.status_code == 200
        assert 'Ammunition' in resp.data.decode()

    def test_does_not_show_child_groups(self, client, db):
        parent = make_market_group(db, cpp_market_group_id=1, name='Parent')
        make_market_group(db, cpp_market_group_id=2, name='Child', parent=parent)
        db.session.commit()
        resp = client.get('/market_groups')
        assert b'Parent' in resp.data
        assert b'Child' not in resp.data
