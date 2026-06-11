"""Tests for evebs/routes/jita_market_analytics.py."""
from evebs.models import JitaMarketAnalytics
from tests.factories import make_item


def _add_analytics(db, item_id, min_sell_price=None, forecast=None):
    db.session.add(JitaMarketAnalytics(
        id=item_id, min_sell_price=min_sell_price, price_forecast_3d=forecast,
    ))


class TestJitaMarketAnalyticsShow:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/jita_market_analytics')
        assert resp.status_code == 302

    def test_returns_200_empty(self, auth_client):
        client, _ = auth_client
        resp = client.get('/jita_market_analytics')
        assert resp.status_code == 200

    def test_lists_item(self, db, auth_client):
        client, _ = auth_client
        make_item(db, item_id=34, name='Tritanium', slug='tritanium')
        _add_analytics(db, 34, min_sell_price=5.5, forecast=6.0)
        db.session.commit()

        resp = client.get('/jita_market_analytics')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data

    def test_search_filters_by_name(self, db, auth_client):
        client, _ = auth_client
        make_item(db, item_id=34, name='Tritanium', slug='tritanium')
        make_item(db, item_id=35, name='Pyerite', slug='pyerite')
        _add_analytics(db, 34, min_sell_price=5.5)
        _add_analytics(db, 35, min_sell_price=12.0)
        db.session.commit()

        resp = client.get('/jita_market_analytics?q=pyer')
        assert resp.status_code == 200
        assert b'Pyerite' in resp.data
        assert b'Tritanium' not in resp.data
