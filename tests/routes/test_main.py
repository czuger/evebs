"""Tests for evebs/routes/main.py."""


class TestMainIndex:
    def test_returns_200_when_unauthenticated(self, client):
        resp = client.get('/')
        assert resp.status_code == 200

    def test_redirects_authenticated_user_to_buy_orders(self, auth_client):
        client, _ = auth_client
        resp = client.get('/')
        assert resp.status_code == 302
        assert 'buy_orders' in resp.location
