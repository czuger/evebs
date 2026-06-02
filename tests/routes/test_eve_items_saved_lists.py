"""Tests for evebs/routes/eve_items_saved_lists.py."""
import pytest
from tests.factories import make_item, make_market_group, make_saved_list


class TestSavedListsIndex:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/eve_items_saved_lists')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        resp = client.get('/eve_items_saved_lists')
        assert resp.status_code == 200

    def test_shows_user_lists(self, db, auth_client):
        client, user = auth_client
        make_saved_list(db, user, description='My Minerals')
        db.session.commit()

        resp = client.get('/eve_items_saved_lists')
        assert b'My Minerals' in resp.data


class TestSavedListsCreate:
    def test_redirects_unauthenticated(self, client):
        resp = client.post('/eve_items_saved_lists', data={'description': 'x'})
        assert resp.status_code == 302

    def test_creates_list_with_current_items(self, db, auth_client):
        client, user = auth_client
        mg = make_market_group(db, group_id=1, name='Minerals')
        item = make_item(db, item_id=34, slug='tritanium', market_group=mg)
        db.session.commit()
        user.eve_items.append(item)
        db.session.commit()

        resp = client.post('/eve_items_saved_lists', data={'description': 'My Minerals'})
        assert resp.status_code == 302

        from evebs.models import EveItemsSavedList
        sl = EveItemsSavedList.query.filter_by(user_id=user.id).first()
        assert sl is not None
        assert sl.description == 'My Minerals'
        assert item.id in sl.get_ids()

    def test_empty_description_redirects_to_new(self, auth_client):
        client, _ = auth_client
        resp = client.post('/eve_items_saved_lists', data={'description': ''})
        assert resp.status_code == 302
        assert 'new' in resp.location


class TestSavedListsLoad:
    def test_redirects_unauthenticated(self, client, db):
        resp = client.get('/eve_items_saved_lists/1/load')
        assert resp.status_code == 302

    def test_replaces_current_items_with_saved_ids(self, db, auth_client):
        client, user = auth_client
        mg = make_market_group(db, group_id=1, name='Minerals')
        item1 = make_item(db, item_id=34, slug='tritanium', market_group=mg)
        item2 = make_item(db, item_id=35, slug='pyerite', market_group=mg)
        sl = make_saved_list(db, user, description='Saved', item_ids=[item1.id])
        user.eve_items.append(item2)
        db.session.commit()

        resp = client.get(f'/eve_items_saved_lists/{sl.id}/load')
        assert resp.status_code == 302

        db.session.expire(user)
        item_ids = [i.id for i in user.eve_items]
        assert item1.id in item_ids
        assert item2.id not in item_ids

    def test_404_for_other_users_list(self, db, auth_client):
        from evebs.models import User
        client, user = auth_client
        other = User(uid='999', name='Other', provider='p',
                     token='t', renew_token='r', initialization_finalized=True)
        db.session.add(other)
        db.session.flush()
        sl = make_saved_list(db, other, description='Other list')
        db.session.commit()

        resp = client.get(f'/eve_items_saved_lists/{sl.id}/load')
        assert resp.status_code == 404


class TestSavedListsClear:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/eve_items_saved_lists/clear')
        assert resp.status_code == 302

    def test_clears_user_items(self, db, auth_client):
        client, user = auth_client
        mg = make_market_group(db, group_id=1, name='Minerals')
        item = make_item(db, item_id=34, slug='tritanium', market_group=mg)
        db.session.commit()
        user.eve_items.append(item)
        db.session.commit()

        resp = client.get('/eve_items_saved_lists/clear')
        assert resp.status_code == 302

        db.session.expire(user)
        assert user.eve_items == []


class TestSavedListsDelete:
    def test_redirects_unauthenticated(self, client, db):
        resp = client.post('/eve_items_saved_lists/1/delete')
        assert resp.status_code == 302

    def test_deletes_own_list(self, db, auth_client):
        client, user = auth_client
        sl = make_saved_list(db, user, description='To Delete')
        db.session.commit()
        sl_id = sl.id

        resp = client.post(f'/eve_items_saved_lists/{sl_id}/delete')
        assert resp.status_code == 302

        from evebs.models import EveItemsSavedList
        assert EveItemsSavedList.query.get(sl_id) is None

    def test_404_for_other_users_list(self, db, auth_client):
        from evebs.models import User
        client, user = auth_client
        other = User(uid='999', name='Other', provider='p',
                     token='t', renew_token='r', initialization_finalized=True)
        db.session.add(other)
        db.session.flush()
        sl = make_saved_list(db, other, description='Not mine')
        db.session.commit()

        resp = client.post(f'/eve_items_saved_lists/{sl.id}/delete')
        assert resp.status_code == 404
