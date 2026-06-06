"""Tests for evebs/routes/jita_reactions.py."""
from tests.factories import make_item, make_blueprint


class TestJitaReactionsShow:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/jita_reactions')
        assert resp.status_code == 302

    def test_returns_200_with_no_blueprints(self, auth_client):
        client, _ = auth_client
        resp = client.get('/jita_reactions')
        assert resp.status_code == 200

    def test_returns_200_with_reaction_blueprint(self, db, auth_client):
        """SQL query against JitaManufacturingMargins executes (returns 0 rows)."""
        client, user = auth_client

        item = make_item(db, item_id=35, slug='fullerite-rxn', name='Fullerite')
        bp = make_blueprint(db, item, manufacturing_cost=1000.0)
        bp.activity_type = 'reaction'
        user.blueprints.append(bp)
        db.session.commit()

        resp = client.get('/jita_reactions')
        assert resp.status_code == 200
