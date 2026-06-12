"""Tests for evebs/routes/reaction_lists.py."""
from tests.factories import make_item

from evebs.models import ReactionList


class TestReactionLists:
    def test_edit_redirects_unauthenticated(self, client):
        assert client.get('/reaction_lists/edit').status_code == 302

    def test_edit_returns_200(self, auth_client):
        client, _ = auth_client
        assert client.get('/reaction_lists/edit').status_code == 200

    def test_create_adds_and_dedups(self, db, auth_client):
        client, user = auth_client
        item = make_item(db, item_id=16679, slug='fullerides', name='Fullerides')
        db.session.commit()

        client.post('/reaction_lists', data={'eve_item_id': item.id, 'runs_count': 3})
        client.post('/reaction_lists', data={'eve_item_id': item.id, 'runs_count': 9})  # dedup

        rows = ReactionList.query.filter_by(user_id=user.id, eve_item_id=item.id).all()
        assert len(rows) == 1
        assert rows[0].runs_count == 3

    def test_update_runs_and_remove(self, db, auth_client):
        client, user = auth_client
        item = make_item(db, item_id=16679, slug='fullerides', name='Fullerides')
        db.session.commit()
        client.post('/reaction_lists', data={'eve_item_id': item.id, 'runs_count': 1})
        rl = ReactionList.query.filter_by(user_id=user.id, eve_item_id=item.id).first()

        client.post('/reaction_lists/update', data={f'runs_count_{rl.id}': '7'})
        db.session.expire(rl)
        assert ReactionList.query.get(rl.id).runs_count == 7

        client.post('/remove_reaction_list_check', data={'eve_item_id': item.id})
        assert ReactionList.query.filter_by(user_id=user.id, eve_item_id=item.id).count() == 0
