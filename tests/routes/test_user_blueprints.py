from tests.factories import make_item, make_blueprint


class TestUserBlueprintsShow:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/user_blueprints')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        resp = client.get('/user_blueprints')
        assert resp.status_code == 200

    def test_empty_state_renders(self, auth_client):
        client, _ = auth_client
        resp = client.get('/user_blueprints')
        assert b'No blueprints' in resp.data
