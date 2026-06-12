"""Tests for evebs/routes/sales_details.py."""
from datetime import date

from tests.factories import make_universe_system, make_item, make_sales_final

JITA = 30000142


class TestSalesDetailsShow:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/sales_details/34')
        assert resp.status_code == 302

    def test_404_for_missing_item(self, auth_client):
        client, _ = auth_client
        resp = client.get('/sales_details/999999')
        assert resp.status_code == 404

    def test_lists_sales_for_item(self, db, auth_client):
        client, _ = auth_client
        jita = make_universe_system(db, system_id=JITA, name='Jita')
        item = make_item(db, item_id=34, slug='tritanium', name='Tritanium')
        make_sales_final(db, item, jita, day=date(2026, 6, 10), volume=500, price=12.5, order_id=111)
        make_sales_final(db, item, jita, day=date(2026, 6, 11), volume=700, price=13.0, order_id=222)
        db.session.commit()

        resp = client.get(f'/sales_details/{item.id}')
        assert resp.status_code == 200
        body = resp.data
        assert b'Tritanium' in body
        assert b'Sales details' in body
        assert b'Jita' in body
        assert b'111' in body and b'222' in body

    def test_empty_when_no_sales(self, db, auth_client):
        client, _ = auth_client
        item = make_item(db, item_id=35, slug='ammo', name='Ammo')
        db.session.commit()

        resp = client.get(f'/sales_details/{item.id}')
        assert resp.status_code == 200
        assert b'No recorded sales for this item.' in resp.data
