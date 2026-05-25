"""Tests for evebs/routes/user_sales_orders.py."""


class TestUserSalesOrdersShow:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/user_sales_orders')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        resp = client.get('/user_sales_orders')
        assert resp.status_code == 200

    def test_empty_list_renders(self, auth_client):
        client, _ = auth_client
        resp = client.get('/user_sales_orders')
        assert b'No orders.' in resp.data


class TestUserSalesOrdersUpdate:
    def test_redirects_unauthenticated(self, client):
        resp = client.post('/user_sales_orders/update', data={'sales_orders_show_margin_min': '5'})
        assert resp.status_code == 302

    def test_updates_margin_and_redirects(self, db, auth_client):
        client, user = auth_client
        resp = client.post('/user_sales_orders/update',
                           data={'sales_orders_show_margin_min': '10'})
        assert resp.status_code == 302
        db.session.refresh(user)
        assert user.sales_orders_show_margin_min == 10
