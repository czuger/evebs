"""Tests for evebs/routes/list_items.py."""
import pytest
from tests.factories import make_market_group, make_item


class TestListItemsShow:
    def test_returns_200_without_auth(self, client, db):
        resp = client.get('/list_items')
        assert resp.status_code == 200

    def test_shows_root_market_groups(self, db, client):
        make_market_group(db, group_id=1, name='Minerals')
        make_market_group(db, group_id=2, name='Ships')
        db.session.commit()

        resp = client.get('/list_items')
        assert resp.status_code == 200
        assert b'Minerals' in resp.data
        assert b'Ships' in resp.data

    def test_shows_items_for_leaf_group(self, db, client):
        mg = make_market_group(db, group_id=1, name='Minerals')
        make_item(db, item_id=34, slug='tritanium', market_group=mg)
        db.session.commit()

        resp = client.get(f'/list_items?group_id={mg.id}')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data

    def test_shows_children_for_non_leaf_group(self, db, client):
        parent = make_market_group(db, group_id=1, name='Materials')
        child = make_market_group(db, group_id=2, name='Minerals', parent=parent)
        db.session.commit()

        resp = client.get(f'/list_items?group_id={parent.id}')
        assert resp.status_code == 200
        assert b'Minerals' in resp.data

    def test_404_for_nonexistent_group(self, db, client):
        resp = client.get('/list_items?group_id=9999')
        assert resp.status_code == 404


class TestSelectionChange:
    def test_redirects_unauthenticated(self, client, db):
        resp = client.post('/list_items/selection_change',
                           data={'id': 1, 'check_state': 'true'})
        assert resp.status_code == 302

    def test_adds_item_to_user_watch_list(self, db, auth_client):
        mg = make_market_group(db, group_id=1, name='Minerals')
        item = make_item(db, item_id=34, slug='tritanium', market_group=mg)
        db.session.commit()

        client, user = auth_client
        resp = client.post('/list_items/selection_change',
                           data={'id': item.id, 'check_state': 'true'})
        assert resp.status_code == 200
        resp_json = resp.get_json()
        assert resp_json == {'ok': True}

        from evebs.models import User
        db.session.expire(user)
        assert item in user.eve_items

    def test_removes_item_from_user_watch_list(self, db, auth_client):
        mg = make_market_group(db, group_id=1, name='Minerals')
        item = make_item(db, item_id=34, slug='tritanium', market_group=mg)
        db.session.commit()

        client, user = auth_client
        user.eve_items.append(item)
        db.session.commit()

        resp = client.post('/list_items/selection_change',
                           data={'id': item.id, 'check_state': 'false'})
        assert resp.status_code == 200

        db.session.expire(user)
        assert item not in user.eve_items
