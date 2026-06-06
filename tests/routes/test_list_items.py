"""Tests for evebs/routes/list_items.py."""
import pytest
from tests.factories import make_market_group, make_item, make_universe_system, make_trade_hub


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
                           data={'ids': item.id, 'check_state': 'true'})
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
                           data={'ids': item.id, 'check_state': 'false'})
        assert resp.status_code == 200

        db.session.expire(user)
        assert item not in user.eve_items


class TestListItemsAuthenticatedShow:
    def test_authenticated_user_item_ids_loaded(self, db, auth_client):
        mg = make_market_group(db, group_id=10, name='Minerals')
        item = make_item(db, item_id=34, slug='trit-auth', market_group=mg)
        db.session.commit()

        client, user = auth_client
        user.eve_items.append(item)
        db.session.commit()

        resp = client.get(f'/list_items?group_id={mg.id}')
        assert resp.status_code == 200


class TestSelectGroup:
    def test_adds_all_items_in_leaf_group(self, db, auth_client):
        mg = make_market_group(db, group_id=11, name='Minerals 2')
        item1 = make_item(db, item_id=40, slug='trit-sg', market_group=mg)
        item2 = make_item(db, item_id=41, slug='pye-sg', market_group=mg)
        db.session.commit()

        client, user = auth_client
        resp = client.post('/list_items/select_group', data={'group_id': mg.id})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['count'] == 2

        db.session.expire(user)
        assert item1 in user.eve_items
        assert item2 in user.eve_items

    def test_recurses_into_child_groups(self, db, auth_client):
        parent = make_market_group(db, group_id=12, name='Materials')
        child = make_market_group(db, group_id=13, name='Minerals 3', parent=parent)
        item = make_item(db, item_id=42, slug='trit-rec', market_group=child)
        db.session.commit()

        client, _ = auth_client
        resp = client.post('/list_items/select_group', data={'group_id': parent.id})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['count'] == 1

    def test_redirects_unauthenticated(self, client, db):
        resp = client.post('/list_items/select_group', data={'group_id': 1})
        assert resp.status_code == 302
