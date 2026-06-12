"""Tests for evebs/routes/price_forecasts.py + the dual-window forecast materialized views."""
from datetime import date, timedelta

from sqlalchemy import text

from tests.factories import make_item, make_universe_system, make_sales_final

JITA = 30000142


def _refresh(db):
    db.session.execute(text('REFRESH MATERIALIZED VIEW jita_price_forecast_linear_regression'))
    db.session.execute(text('REFRESH MATERIALIZED VIEW jita_volume_forecast_linear_regression'))
    db.session.commit()


def _seed_sales(db, item, jita, n_days=12, base_price=100.0, p_slope=5.0, base_vol=1000):
    """Two Jita sales per day over the last n_days, with a clean upward price/volume trend.

    Spans 12 days so the 30-day window has data distinct from the 7-day window.
    """
    today = date.today()
    oid = item.id * 1000
    for i in range(n_days):
        d = today - timedelta(days=n_days - i)
        for vol, bump in ((base_vol + 100 * i, 0.0), (base_vol // 2, 2.0)):
            make_sales_final(db, item, jita, day=d, volume=vol,
                             price=base_price + p_slope * i + bump, order_id=oid)
            oid += 1


class TestPriceForecasts:
    def test_list_and_detail(self, db, auth_client):
        client, _ = auth_client
        jita = make_universe_system(db, system_id=JITA, name='Jita')
        item = make_item(db, item_id=34, name='Tritanium', slug='tritanium')
        _seed_sales(db, item, jita)
        db.session.commit()
        _refresh(db)

        # Both windows populated for the item at the +3d horizon (the furthest forecast day).
        row = db.session.execute(text(
            'SELECT forecast_7d, forecast_30d, spread, spread_percent '
            'FROM jita_price_forecast_linear_regression '
            'WHERE type_id = :t AND forecast_date = CURRENT_DATE + 3'), {'t': item.id}).first()
        assert row is not None
        assert row.forecast_7d is not None and row.forecast_30d is not None
        assert row.spread >= 0 and row.spread_percent >= 0

        resp = client.get('/price_forecasts')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data
        assert b'Price (+3d)' in resp.data and b'Volume (+3d)' in resp.data   # both column groups
        assert b'|Spread %|' in resp.data
        assert b'7d win' in resp.data and b'30d win' in resp.data

        resp = client.get(f'/price_forecasts/{item.id}')
        assert resp.status_code == 200
        assert b'priceChart' in resp.data
        assert b'volChart' in resp.data
        assert b'7-day window' in resp.data
        assert b'30-day window' in resp.data
        assert b'Price forecast (next 3 days)' in resp.data
        assert b'Volume forecast (next 3 days)' in resp.data

    def test_redirects_unauthenticated(self, db, client):
        resp = client.get('/price_forecasts')
        assert resp.status_code == 302

    def test_detail_no_data(self, db, auth_client):
        client, _ = auth_client
        make_universe_system(db, system_id=JITA, name='Jita')
        item = make_item(db, item_id=34, slug='trit', name='Trit')
        db.session.commit()
        _refresh(db)

        resp = client.get(f'/price_forecasts/{item.id}')
        assert resp.status_code == 200
        assert b'No price forecast available' in resp.data
        assert b'Trit' not in client.get('/price_forecasts').data   # not listed

    def test_detail_404_for_missing_item(self, db, auth_client):
        client, _ = auth_client
        resp = client.get('/price_forecasts/999999')
        assert resp.status_code == 404
