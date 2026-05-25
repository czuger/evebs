"""Tests for evebs/routes/choose_trade_hubs.py."""
import pytest
from tests.factories import make_region, make_trade_hub


@pytest.fixture
def hubs(db):
    region = make_region(db)
    outer = make_trade_hub(db, region, system_id=30000142, name='Jita', inner=False)
    inner = make_trade_hub(db, region, system_id=30000144, name='Perimeter', inner=True)
    db.session.commit()
    return {'region': region, 'outer': outer, 'inner': inner}


class TestChooseTradeHubsEdit:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/choose_trade_hubs/edit')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        resp = client.get('/choose_trade_hubs/edit')
        assert resp.status_code == 200

    def test_shows_trade_hubs(self, db, auth_client, hubs):
        client, _ = auth_client
        resp = client.get('/choose_trade_hubs/edit')
        assert resp.status_code == 200
        assert b'Jita' in resp.data
        assert b'Perimeter' in resp.data


class TestChooseTradeHubsUpdate:
    def test_redirects_unauthenticated(self, client, db):
        resp = client.post('/choose_trade_hubs/update', data={'id': 1, 'check_state': 'true'})
        assert resp.status_code == 302

    def test_adds_hub_to_user(self, db, auth_client, hubs):
        client, user = auth_client
        resp = client.post('/choose_trade_hubs/update', data={
            'id': hubs['outer'].id,
            'check_state': 'true',
        })
        assert resp.status_code == 200

        db.session.expire(user)
        assert hubs['outer'] in user.trade_hubs

    def test_removes_hub_from_user(self, db, auth_client, hubs):
        client, user = auth_client
        user.trade_hubs.append(hubs['outer'])
        db.session.commit()

        resp = client.post('/choose_trade_hubs/update', data={
            'id': hubs['outer'].id,
            'check_state': 'false',
        })
        assert resp.status_code == 200

        db.session.expire(user)
        assert hubs['outer'] not in user.trade_hubs

    def test_404_for_nonexistent_hub(self, db, auth_client):
        client, _ = auth_client
        resp = client.post('/choose_trade_hubs/update', data={'id': 9999, 'check_state': 'true'})
        assert resp.status_code == 404
