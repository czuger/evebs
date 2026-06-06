"""Tests for evebs/routes/invention_lists.py."""
import pytest
from tests.factories import make_universe_system, make_trade_hub, make_item


@pytest.fixture
def seeded(db):
    system = make_universe_system(db)
    hub = make_trade_hub(db, system)
    item = make_item(db, item_id=34, slug='tritanium')
    db.session.commit()
    return {'hub': hub, 'item': item}


class TestInventionListEdit:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/invention_lists/edit')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        resp = client.get('/invention_lists/edit')
        assert resp.status_code == 200


class TestInventionListCreate:
    def test_creates_entry_and_redirects(self, db, auth_client, seeded):
        client, user = auth_client
        resp = client.post('/invention_lists', data={
            'eve_item_id': seeded['item'].id,
            'universe_system_id': seeded['hub'].id,
            'runs_count': 5,
        })
        assert resp.status_code == 302

        from evebs.models import InventionList
        il = InventionList.query.filter_by(user_id=user.id).first()
        assert il is not None
        assert il.runs_count == 5

    def test_prevents_duplicates(self, db, auth_client, seeded):
        client, user = auth_client
        for _ in range(2):
            client.post('/invention_lists', data={
                'eve_item_id': seeded['item'].id,
                'universe_system_id': seeded['hub'].id,
            })

        from evebs.models import InventionList
        assert InventionList.query.filter_by(user_id=user.id).count() == 1

    def test_redirects_unauthenticated(self, client, seeded):
        resp = client.post('/invention_lists', data={
            'eve_item_id': seeded['item'].id,
            'universe_system_id': seeded['hub'].id,
        })
        assert resp.status_code == 302


class TestInventionListRemoveCheck:
    def test_deletes_entry_and_returns_204(self, db, auth_client, seeded):
        from evebs.models import InventionList
        client, user = auth_client
        il = InventionList(
            user_id=user.id,
            eve_item_id=seeded['item'].id,
            universe_system_id=seeded['hub'].id,
            runs_count=1,
        )
        db.session.add(il)
        db.session.commit()

        resp = client.post('/remove_invention_list_check', data={
            'universe_system_id': seeded['hub'].id,
            'eve_item_id': seeded['item'].id,
        })
        assert resp.status_code == 204
        assert InventionList.query.filter_by(user_id=user.id).count() == 0

    def test_redirects_unauthenticated(self, client, db):
        resp = client.post('/remove_invention_list_check',
                           data={'universe_system_id': 1, 'eve_item_id': 1})
        assert resp.status_code == 302
