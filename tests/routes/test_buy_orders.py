"""Tests for evebs/routes/buy_orders.py."""
import pytest


class TestBuyOrders:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/buy_orders')
        assert resp.status_code == 302
        assert 'login' in resp.location.lower() or '/' in resp.location

    def test_returns_200_for_authenticated_user(self, auth_client):
        client, _ = auth_client
        resp = client.get('/buy_orders')
        assert resp.status_code == 200

    def test_pagination_param_accepted(self, auth_client):
        client, _ = auth_client
        resp = client.get('/buy_orders?page=1')
        assert resp.status_code == 200

    def test_batch_cap_off_still_renders(self, db, client, user):
        user.batch_cap = False
        db.session.commit()
        from tests.conftest import _log_in
        _log_in(client, user.id)
        resp = client.get('/buy_orders')
        assert resp.status_code == 200
