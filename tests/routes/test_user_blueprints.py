from unittest.mock import patch

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


class TestUserBlueprintsRefresh:
    def test_redirects_unauthenticated(self, client):
        resp = client.post('/user_blueprints/refresh')
        assert resp.status_code == 302

    def test_refresh_populates_blueprints_and_redirects(self, db, auth_client):
        item = make_item(db, item_id=34, slug='trit')
        bp = make_blueprint(db, item, blueprint_id=11399)
        db.session.commit()

        client, user = auth_client
        with patch('esi.download_my_blueprints.EsiClient') as MockClient:
            instance = MockClient.return_value
            instance.set_auth_token.return_value = True
            instance.get_all_pages.return_value = [{'type_id': bp.id}]
            resp = client.post('/user_blueprints/refresh')

        assert resp.status_code == 302
        db.session.refresh(user)
        assert bp in user.blueprints

    def test_refresh_with_unknown_type_ids_inserts_nothing(self, db, auth_client):
        client, user = auth_client
        with patch('esi.download_my_blueprints.EsiClient') as MockClient:
            instance = MockClient.return_value
            instance.set_auth_token.return_value = True
            instance.get_all_pages.return_value = [{'type_id': 99999999}]
            client.post('/user_blueprints/refresh')

        db.session.refresh(user)
        assert user.blueprints == []
