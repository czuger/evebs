"""Tests for evebs/routes/components_to_buys.py."""


class TestComponentsToBuysShow:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/components_to_buys')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        resp = client.get('/components_to_buys')
        assert resp.status_code == 200

    def test_empty_list_renders(self, auth_client):
        client, _ = auth_client
        resp = client.get('/components_to_buys')
        assert b'Nothing to buy.' in resp.data
