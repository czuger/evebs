"""Tests for evebs/routes/reaction_lists.py."""
from tests.factories import make_item, make_blueprint

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

    def test_edit_shows_decompose_tree_for_sub_reactions(self, db, auth_client):
        client, user = auth_client
        make_item(db, item_id=34, slug='raw', name='Raw Mat')
        sub = make_item(db, item_id=100, slug='subrxn', name='Sub Rxn')
        root = make_item(db, item_id=200, slug='rootrxn', name='Root Rxn')

        sub_bp = make_blueprint(db, sub, blueprint_id=1100, prod_qtt=10)
        sub_bp.activity_type = 'reaction'
        sub_bp.manufacturing_tree = {'34': {'quantity': 50, 'name': 'Raw Mat', 'chain': {}}}

        root_bp = make_blueprint(db, root, blueprint_id=1200, prod_qtt=5)
        root_bp.activity_type = 'reaction'
        root_bp.manufacturing_tree = {
            '100': {'quantity': 20, 'name': 'Sub Rxn',
                    'chain': {'34': {'quantity': 50, 'name': 'Raw Mat', 'chain': {}}}},
            '34': {'quantity': 5, 'name': 'Raw Mat', 'chain': {}},
        }
        db.session.add(ReactionList(user_id=user.id, eve_item_id=root.id, runs_count=2))
        db.session.commit()

        body = client.get('/reaction_lists/edit').get_data(as_text=True)
        assert 'Decompose' in body
        assert 'Sub Rxn' in body
        assert 'name="sub_item" value="100"' in body          # sub-reaction is checkable
        assert 'name="sub_item" value="34"' not in body       # raw material is not

    def test_add_subreactions_adds_with_runs_and_dedups(self, db, auth_client):
        client, user = auth_client
        make_item(db, item_id=100, slug='subrxn', name='Sub Rxn')
        db.session.commit()

        client.post('/reaction_lists/add_subreactions',
                    data={'sub_item': '100', 'sub_runs_100': '4'})
        rl = ReactionList.query.filter_by(user_id=user.id, eve_item_id=100).first()
        assert rl is not None and rl.runs_count == 4

        client.post('/reaction_lists/add_subreactions',
                    data={'sub_item': '100', 'sub_runs_100': '9'})  # dedup
        assert ReactionList.query.filter_by(user_id=user.id, eve_item_id=100).count() == 1
