"""Tests for evebs/routes/jita_reactions.py."""
from datetime import date, timedelta

from sqlalchemy import text

from tests.factories import (
    make_universe_system, make_item, make_blueprint, make_jita_min_price, make_sales_final,
)

JITA = 30000142


def _refresh_price_forecast(db):
    db.session.execute(text('REFRESH MATERIALIZED VIEW jita_price_forecast_linear_regression'))
    db.session.commit()


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
        user.reaction_modifications = {'system_cost_index': 5, 'scc_tax': 4,
                                       'reaction_tax': 1, 'material_consumption': 0}
        user.sales_taxes = {'broker_fee_taxes': 3, 'sales_taxes': 2, 'safety_tax': 0}

        jita = make_universe_system(db, system_id=JITA, name='Jita')
        mat = make_item(db, item_id=34, slug='hydrogen', name='Hydrogen')
        prod = make_item(db, item_id=35, slug='fullerite-rxn', name='Fullerite')
        bp = make_blueprint(db, prod, blueprint_id=20035, nb_runs=1, prod_qtt=10)
        bp.activity_type = 'reaction'
        bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Hydrogen', 'chain': {}}}
        make_jita_min_price(db, mat, min_sell_price=5.0)      # materials priced -> uic row
        make_jita_min_price(db, prod, min_sell_price=900.0)   # product: uic jma_prod + live sell
        make_sales_final(db, prod, jita, volume=1234, price=900.0, day=date.today(), order_id=7)
        user.blueprints.append(bp)
        db.session.commit()

        resp = client.get('/jita_reactions')
        assert resp.status_code == 200
        body = resp.data
        assert b'Fullerite' in body
        assert b'Reaction cost / item' in body
        assert b'Benefit per batch' in body
        assert b'Sold (7d)' in body                              # 7-day sold column
        assert b'Tendency' in body                               # tendency column
        assert b'table-success' in body                         # benefit > 0
        assert b'streamline-ultimate:chemical-hexagon-1' in body  # owned icon
        assert b'/reaction_lists' in body                       # add-to-reaction-list form

    def test_tendency_up_when_forecast_above_current(self, db, auth_client):
        """Tendency is 'up' (▲) when the +3d price forecast exceeds the current price by >10%."""
        client, user = auth_client
        jita = make_universe_system(db, system_id=JITA, name='Jita')
        mat = make_item(db, item_id=34, slug='hydro', name='Hydrogen')
        prod = make_item(db, item_id=35, slug='fullerite-up', name='Fullerite Up')
        bp = make_blueprint(db, prod, blueprint_id=20035, nb_runs=1, prod_qtt=10)
        bp.activity_type = 'reaction'
        bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Hydrogen', 'chain': {}}}
        make_jita_min_price(db, mat, min_sell_price=5.0)
        make_jita_min_price(db, prod, min_sell_price=100.0)   # current price low
        # Rising Jita sales well above the current price → forecast >> current.
        today = date.today()
        for i in range(6):
            make_sales_final(db, prod, jita, day=today - timedelta(days=6 - i),
                             volume=1000, price=1000.0 + 10.0 * i, order_id=900 + i)
        db.session.commit()
        _refresh_price_forecast(db)

        body = client.get('/jita_reactions').get_data(as_text=True)
        assert 'Fullerite Up' in body
        assert '&#9650;' in body            # up arrow rendered

    def test_tendency_slow_up_within_inner_band(self, db, auth_client):
        """Tendency is 'slow_up' (△) when the forecast is +0.1%..+5% above the current price."""
        client, user = auth_client
        jita = make_universe_system(db, system_id=JITA, name='Jita')
        mat = make_item(db, item_id=34, slug='hydro2', name='Hydrogen')
        prod = make_item(db, item_id=35, slug='fullerite-slow', name='Fullerite Slow')
        bp = make_blueprint(db, prod, blueprint_id=20035, nb_runs=1, prod_qtt=10)
        bp.activity_type = 'reaction'
        bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Hydrogen', 'chain': {}}}
        make_jita_min_price(db, mat, min_sell_price=5.0)
        make_jita_min_price(db, prod, min_sell_price=980.0)   # current ≈ 0.98 × forecast
        # Flat Jita sales at 1000 → forecast ≈ 1000; 1000 / 980 ≈ 1.02 → slow_up.
        today = date.today()
        for i in range(6):
            make_sales_final(db, prod, jita, day=today - timedelta(days=6 - i),
                             volume=1000, price=1000.0, order_id=950 + i)
        db.session.commit()
        _refresh_price_forecast(db)

        body = client.get('/jita_reactions').get_data(as_text=True)
        assert 'Fullerite Slow' in body
        assert '&#9651;' in body            # hollow up triangle (slow growth)
        assert '&#9650;' not in body        # not the strong up arrow
