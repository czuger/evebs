"""Tests for evebs/routes/sell_orders.py.

The route values items against the 3-day Jita price forecast
(jita_price_forecast_linear_regression.forecast_7d at CURRENT_DATE + 3) and shows the
matching Jita volume forecast — it no longer depends on trade hubs or live sell orders.
"""
from datetime import date, timedelta

from sqlalchemy import text

from tests.factories import (
    make_universe_system, make_item, make_blueprint, make_jita_min_price, make_sales_final,
)

JITA = 30000142


def _refresh(db):
    db.session.execute(text('REFRESH MATERIALIZED VIEW jita_price_forecast_linear_regression'))
    db.session.execute(text('REFRESH MATERIALIZED VIEW jita_volume_forecast_linear_regression'))
    db.session.commit()


def _seed_sales(db, item, jita, n_days=6, base_price=1000.0, p_slope=10.0, base_vol=2000):
    """Two Jita sales per day over the last n_days with a clean upward price/volume trend."""
    today = date.today()
    oid = item.id * 1000
    for i in range(n_days):
        d = today - timedelta(days=n_days - i)
        for vol, bump in ((base_vol + 100 * i, 0.0), (base_vol // 2, 2.0)):
            make_sales_final(db, item, jita, day=d, volume=vol,
                             price=base_price + p_slope * i + bump, order_id=oid)
            oid += 1


class TestSellOrdersShow:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/sell_orders')
        assert resp.status_code == 302

    def test_returns_200_with_nothing_seeded(self, auth_client):
        client, _ = auth_client
        resp = client.get('/sell_orders')
        assert resp.status_code == 200

    def test_lists_item_priced_against_forecast(self, db, auth_client):
        """A manufacturable item with a Jita forecast appears, priced from forecast_7d, with
        no trade-hub column."""
        client, user = auth_client
        user.sell_orders_filtering = {'min_margin_percent': 0, 'min_batch_margin_amount': 0}

        jita = make_universe_system(db, system_id=JITA, name='Jita')
        mat = make_item(db, item_id=34, slug='tritanium', name='Tritanium')
        prod = make_item(db, item_id=35, slug='ammo-sell', name='Ammo Sell')
        bp = make_blueprint(db, prod, blueprint_id=10035, nb_runs=1, prod_qtt=10)
        bp.activity_type = 'manufacturing'
        bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Tritanium', 'chain': {}}}
        make_jita_min_price(db, mat, min_sell_price=5.0)     # materials priced -> uic row exists
        make_jita_min_price(db, prod, min_sell_price=900.0)  # product priced -> view's jma_prod join
        _seed_sales(db, prod, jita)                          # Jita forecast for the product
        db.session.commit()
        _refresh(db)

        # Forecast values the route should surface at the +3d horizon.
        price_fc = db.session.execute(text(
            'SELECT forecast_7d FROM jita_price_forecast_linear_regression '
            'WHERE type_id = :t AND forecast_date = CURRENT_DATE + 3'), {'t': prod.id}).scalar()
        assert price_fc is not None and price_fc > 0

        resp = client.get('/sell_orders')
        assert resp.status_code == 200
        body = resp.data
        assert b'Ammo Sell' in body
        assert b'Forecast price / unit' in body
        assert b'Forecast vol.' in body
        assert b'<th>Trade hub</th>' not in body   # hub column dropped
