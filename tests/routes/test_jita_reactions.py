"""Tests for evebs/routes/jita_reactions.py.

The route values reactions against MarketProphetForecast (region The Forge, confidence 0.95):
avg_predicted → forecast price, vol_predicted → forecast volume (last forecast day). The
low-quality warning is driven by price_spread_pct and the Tendency column by price_direction —
mirroring /sell_orders, but for activity_type='reaction'.
"""
from datetime import date, timedelta

from evebs.models import MarketProphetForecast
from tests.factories import make_item, make_blueprint, make_jita_min_price

JITA = 30000142
FORGE = 10000002


def _seed_forecast(db, item, price_spread_pct=0.1, price_direction=1, avg=1000.0, vol=2000.0):
    start = date.today()
    for i in range(5):
        db.session.add(MarketProphetForecast(
            region_id=FORGE, type_id=item.id, confidence=0.95,
            forecast_date=start + timedelta(days=i + 1),
            avg_predicted=avg, avg_lower=avg - 50, avg_upper=avg + 50,
            low_predicted=avg - 100, low_lower=avg - 150, low_upper=avg - 50,
            high_predicted=avg + 100, high_lower=avg + 50, high_upper=avg + 150,
            vol_predicted=vol, vol_lower=vol - 100, vol_upper=vol + 100,
            price_spread=200.0, price_spread_pct=price_spread_pct,
            price_direction=price_direction))
    db.session.commit()


class TestJitaReactionsShow:
    def test_redirects_unauthenticated(self, client):
        assert client.get('/jita_reactions').status_code == 302

    def test_returns_200_with_no_blueprints(self, auth_client):
        client, _ = auth_client
        assert client.get('/jita_reactions').status_code == 200

    def test_returns_200_with_reaction_blueprint(self, db, auth_client):
        """SQL query executes (no priced materials → user_industry_costs has no row)."""
        client, user = auth_client
        item = make_item(db, item_id=35, slug='fullerite-rxn', name='Fullerite')
        bp = make_blueprint(db, item, manufacturing_cost=1000.0)
        bp.activity_type = 'reaction'
        user.blueprints.append(bp)
        db.session.commit()

        assert client.get('/jita_reactions').status_code == 200

    def _seed_priced_reaction(self, db, user, price_spread_pct=0.1, price_direction=1):
        user.reaction_modifications = {'system_cost_index': 5, 'scc_tax': 4,
                                       'reaction_tax': 1, 'material_consumption': 0}
        user.sales_taxes = {'broker_fee_taxes': 3, 'sales_taxes': 2, 'safety_tax': 0}
        mat = make_item(db, item_id=34, slug='hydrogen', name='Hydrogen')
        prod = make_item(db, item_id=35, slug='fullerite-rxn', name='Fullerite')
        bp = make_blueprint(db, prod, blueprint_id=20035, nb_runs=1, prod_qtt=10)
        bp.activity_type = 'reaction'
        bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Hydrogen', 'chain': {}}}
        make_jita_min_price(db, mat, min_sell_price=5.0)      # materials priced → uic row
        make_jita_min_price(db, prod, min_sell_price=900.0)   # product priced → uic jma_prod
        _seed_forecast(db, prod, price_spread_pct=price_spread_pct, price_direction=price_direction)
        user.blueprints.append(bp)
        db.session.commit()
        return prod

    def test_lists_owned_reaction_priced_from_forecast(self, db, auth_client):
        """Reaction valued from the Prophet forecast with the sell_orders-style columns."""
        client, user = auth_client
        self._seed_priced_reaction(db, user)

        resp = client.get('/jita_reactions')
        assert resp.status_code == 200
        body = resp.data
        assert b'Fullerite' in body
        assert b'Cost + tax / unit' in body
        assert b'Forecast price / unit' in body
        assert b'Forecast vol.' in body
        assert b'Margin %' in body
        assert b'Batch margin' in body
        assert b'Sold (7d)' in body
        assert b'Tendency' in body
        assert b'/market_forecasts/35' in body                  # forecast price links to detail
        assert b'streamline-ultimate:chemical-hexagon-1' in body  # owned icon
        assert b'/reaction_lists' in body                       # add-to-reaction-list form

    def test_tendency_up_when_price_direction_up(self, db, auth_client):
        client, user = auth_client
        self._seed_priced_reaction(db, user, price_direction=1)
        body = client.get('/jita_reactions').get_data(as_text=True)
        assert 'Fullerite' in body
        assert '&#9650;' in body            # strong up arrow

    def test_tendency_slow_up_when_price_direction_slow_up(self, db, auth_client):
        client, user = auth_client
        self._seed_priced_reaction(db, user, price_direction=2)
        body = client.get('/jita_reactions').get_data(as_text=True)
        assert 'Fullerite' in body
        assert '&#9651;' in body            # hollow up triangle (slow growth)
        assert '&#9650;' not in body        # not the strong up arrow

    def test_low_quality_forecast_shows_warning(self, db, auth_client):
        client, user = auth_client
        self._seed_priced_reaction(db, user, price_spread_pct=0.4)   # Uncertain
        assert b'fa-exclamation-triangle' in client.get('/jita_reactions').data

    def test_high_quality_forecast_has_no_warning(self, db, auth_client):
        client, user = auth_client
        self._seed_priced_reaction(db, user, price_spread_pct=0.05)  # Very Stable
        assert b'fa-exclamation-triangle' not in client.get('/jita_reactions').data
