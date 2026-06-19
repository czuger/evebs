"""Tests for evebs/routes/sell_orders.py.

The route values items against MarketProphetForecast (region The Forge, confidence 0.95):
avg_predicted → forecast price, vol_predicted → forecast volume, taken from the last
forecast day. The low-quality warning/filter is driven by price_spread_pct (>= 0.30 =
Uncertain/Highly Volatile) and the Tendency column by price_direction.
"""
from datetime import date, timedelta

from evebs.models import MarketProphetForecast
from tests.factories import make_item, make_blueprint, make_jita_min_price

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


class TestSellOrdersShow:
    def test_redirects_unauthenticated(self, client):
        assert client.get('/sell_orders').status_code == 302

    def test_returns_200_with_nothing_seeded(self, auth_client):
        client, _ = auth_client
        assert client.get('/sell_orders').status_code == 200

    def _seed_priced_item(self, db, user, price_spread_pct=0.1, price_direction=1):
        user.sell_orders_filtering = {'min_margin_percent': 0, 'min_batch_margin_amount': 0}
        mat = make_item(db, item_id=34, slug='tritanium', name='Tritanium')
        prod = make_item(db, item_id=35, slug='ammo-sell', name='Ammo Sell')
        bp = make_blueprint(db, prod, blueprint_id=10035, nb_runs=1, prod_qtt=10)
        bp.activity_type = 'manufacturing'
        bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Tritanium', 'chain': {}}}
        make_jita_min_price(db, mat, min_sell_price=5.0)      # materials priced → uic row exists
        make_jita_min_price(db, prod, min_sell_price=900.0)   # product priced → view join
        _seed_forecast(db, prod, price_spread_pct=price_spread_pct, price_direction=price_direction)
        db.session.commit()
        return prod

    def test_lists_item_priced_against_forecast(self, db, auth_client):
        client, user = auth_client
        self._seed_priced_item(db, user)
        resp = client.get('/sell_orders')
        assert resp.status_code == 200
        body = resp.data
        assert b'Ammo Sell' in body
        assert b'Forecast price / unit' in body
        assert b'Forecast vol.' in body
        assert b'Tendency' in body
        assert b'Sold (7d)' in body
        assert b'&#9650;' in body                  # price_direction=1 → up tendency
        assert b'/market_forecasts/35' in body     # price links to the forecast detail

    def test_low_quality_shows_warning(self, db, auth_client):
        client, user = auth_client
        self._seed_priced_item(db, user, price_spread_pct=0.4)   # Uncertain
        resp = client.get('/sell_orders')
        assert resp.status_code == 200
        assert b'fa-exclamation-triangle' in resp.data

    def test_high_quality_has_no_warning(self, db, auth_client):
        client, user = auth_client
        self._seed_priced_item(db, user, price_spread_pct=0.05)  # Very Stable
        resp = client.get('/sell_orders')
        assert resp.status_code == 200
        assert b'fa-exclamation-triangle' not in resp.data

    def test_hide_low_quality_filter_excludes_row(self, db, auth_client):
        client, user = auth_client
        self._seed_priced_item(db, user, price_spread_pct=0.4)
        user.sell_orders_filtering = {**user.sell_orders_filtering, 'hide_low_confidence': True}
        db.session.commit()
        resp = client.get('/sell_orders')
        assert resp.status_code == 200
        assert b'Ammo Sell' not in resp.data

    def test_low_quality_kept_when_filter_off(self, db, auth_client):
        client, user = auth_client
        self._seed_priced_item(db, user, price_spread_pct=0.4)
        user.sell_orders_filtering = {**user.sell_orders_filtering, 'hide_low_confidence': False}
        db.session.commit()
        resp = client.get('/sell_orders')
        assert resp.status_code == 200
        assert b'Ammo Sell' in resp.data

    def test_hide_low_quality_keeps_high_quality_row(self, db, auth_client):
        client, user = auth_client
        self._seed_priced_item(db, user, price_spread_pct=0.05)
        user.sell_orders_filtering = {**user.sell_orders_filtering, 'hide_low_confidence': True}
        db.session.commit()
        resp = client.get('/sell_orders')
        assert resp.status_code == 200
        assert b'Ammo Sell' in resp.data
