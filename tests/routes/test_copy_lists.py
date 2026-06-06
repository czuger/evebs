"""Tests for evebs/routes/copy_lists.py."""
import pytest
from tests.factories import make_universe_system, make_trade_hub, make_item


@pytest.fixture
def seeded(db):
    system = make_universe_system(db)
    hub = make_trade_hub(db, system)
    item = make_item(db, item_id=34, slug='tritanium')
    db.session.commit()
    return {'hub': hub, 'item': item}


class TestCopyListEdit:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/copy_lists/edit')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        resp = client.get('/copy_lists/edit')
        assert resp.status_code == 200


class TestCopyListCreate:
    def test_creates_entry_and_redirects(self, db, auth_client, seeded):
        client, user = auth_client
        resp = client.post('/copy_lists', data={
            'eve_item_id': seeded['item'].id,
            'universe_system_id': seeded['hub'].id,
            'runs_count': 3,
        })
        assert resp.status_code == 302

        from evebs.models import CopyList
        cl = CopyList.query.filter_by(user_id=user.id).first()
        assert cl is not None
        assert cl.runs_count == 3

    def test_prevents_duplicates(self, db, auth_client, seeded):
        client, user = auth_client
        for _ in range(2):
            client.post('/copy_lists', data={
                'eve_item_id': seeded['item'].id,
                'universe_system_id': seeded['hub'].id,
            })

        from evebs.models import CopyList
        assert CopyList.query.filter_by(user_id=user.id).count() == 1

    def test_redirects_unauthenticated(self, client, seeded):
        resp = client.post('/copy_lists', data={
            'eve_item_id': seeded['item'].id,
            'universe_system_id': seeded['hub'].id,
        })
        assert resp.status_code == 302


class TestCopyListRemoveCheck:
    def test_deletes_entry_and_returns_204(self, db, auth_client, seeded):
        from evebs.models import CopyList
        client, user = auth_client
        cl = CopyList(
            user_id=user.id,
            eve_item_id=seeded['item'].id,
            universe_system_id=seeded['hub'].id,
            runs_count=1,
        )
        db.session.add(cl)
        db.session.commit()

        resp = client.post('/remove_copy_list_check', data={
            'universe_system_id': seeded['hub'].id,
            'eve_item_id': seeded['item'].id,
        })
        assert resp.status_code == 204
        assert CopyList.query.filter_by(user_id=user.id).count() == 0

    def test_redirects_unauthenticated(self, client, db):
        resp = client.post('/remove_copy_list_check',
                           data={'universe_system_id': 1, 'eve_item_id': 1})
        assert resp.status_code == 302
