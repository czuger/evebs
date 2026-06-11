"""Tests for evebs/routes/jita_min_prices.py."""
from tests.factories import make_item, make_jita_min_price


class TestJitaMinPricesShow:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/jita_min_prices')
        assert resp.status_code == 302

    def test_returns_200_empty(self, auth_client):
        client, _ = auth_client
        resp = client.get('/jita_min_prices')
        assert resp.status_code == 200

    def test_lists_item(self, db, auth_client):
        client, _ = auth_client
        item = make_item(db, item_id=34, name='Tritanium', slug='tritanium')
        make_jita_min_price(db, item, min_sell_price=5.5)
        db.session.commit()

        resp = client.get('/jita_min_prices')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data

    def test_search_filters_by_name(self, db, auth_client):
        client, _ = auth_client
        tri = make_item(db, item_id=34, name='Tritanium', slug='tritanium')
        pye = make_item(db, item_id=35, name='Pyerite', slug='pyerite')
        make_jita_min_price(db, tri, min_sell_price=5.5)
        make_jita_min_price(db, pye, min_sell_price=12.0)
        db.session.commit()

        resp = client.get('/jita_min_prices?q=pyer')
        assert resp.status_code == 200
        assert b'Pyerite' in resp.data
        assert b'Tritanium' not in resp.data
