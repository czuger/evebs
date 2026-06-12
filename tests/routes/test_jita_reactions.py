"""Tests for evebs/routes/jita_reactions.py."""
from tests.factories import (
    make_universe_system, make_item, make_blueprint, make_jita_min_price,
)

JITA = 30000142


class TestJitaReactionsShow:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/jita_reactions')
        assert resp.status_code == 302

    def test_returns_200_with_no_blueprints(self, auth_client):
        client, _ = auth_client
        resp = client.get('/jita_reactions')
        assert resp.status_code == 200

    def test_returns_200_with_reaction_blueprint(self, db, auth_client):
        """SQL query executes (no priced materials → user_industry_costs has no row)."""
        client, user = auth_client

        item = make_item(db, item_id=35, slug='fullerite-rxn', name='Fullerite')
        bp = make_blueprint(db, item, manufacturing_cost=1000.0)
        bp.activity_type = 'reaction'
        user.blueprints.append(bp)
        db.session.commit()

        resp = client.get('/jita_reactions')
        assert resp.status_code == 200

    def test_lists_owned_reaction_priced_from_live_sell(self, db, auth_client):
        """Reaction cost from user_industry_costs (+ the user's reaction tax), est. sell price
        from the live lowest Jita sell order, sell tax from the user's sales_taxes."""
        client, user = auth_client
        user.industry_taxes = {'reaction': {'system_cost_index': 5, 'scc_tax': 4, 'reaction_tax': 1}}
        user.sales_taxes = {'broker_fee_taxes': 3, 'sales_taxes': 2, 'safety_tax': 0}

        make_universe_system(db, system_id=JITA, name='Jita')
        mat = make_item(db, item_id=34, slug='hydrogen', name='Hydrogen')
        prod = make_item(db, item_id=35, slug='fullerite-rxn', name='Fullerite')
        bp = make_blueprint(db, prod, blueprint_id=20035, nb_runs=1, prod_qtt=10)
        bp.activity_type = 'reaction'
        bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Hydrogen', 'chain': {}}}
        make_jita_min_price(db, mat, min_sell_price=5.0)      # materials priced -> uic row
        make_jita_min_price(db, prod, min_sell_price=900.0)   # product: uic jma_prod + live sell
        user.blueprints.append(bp)
        db.session.commit()

        resp = client.get('/jita_reactions')
        assert resp.status_code == 200
        body = resp.data
        assert b'Fullerite' in body
        assert b'Reaction cost / item' in body
        assert b'Benefit per batch' in body
        assert b'table-success' in body                         # benefit > 0
        assert b'streamline-ultimate:chemical-hexagon-1' in body  # owned icon
