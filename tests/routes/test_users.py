"""Tests for evebs/routes/users.py."""
import pytest


class TestUsersEdit:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/users/edit')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        resp = client.get('/users/edit')
        assert resp.status_code == 200


class TestUsersUpdate:
    def test_redirects_unauthenticated(self, client):
        resp = client.post('/users', data={'min_margin_percent': 15})
        assert resp.status_code == 302

    def test_updates_numeric_settings(self, db, auth_client):
        client, user = auth_client
        resp = client.post('/users', data={
            'min_margin_percent':      '25',
            'min_batch_margin_amount': '10000000',
            'batch_cap_multiplier':    '5',
        })
        assert resp.status_code == 302

        db.session.expire(user)
        assert user.sell_orders_filtering['min_margin_percent'] == 25
        assert user.sell_orders_filtering['min_batch_margin_amount'] == 10_000_000
        assert user.batch_cap_multiplier == 5

    def test_enables_batch_cap(self, db, auth_client):
        client, user = auth_client
        client.post('/users', data={'batch_cap': 'on'})
        db.session.expire(user)
        assert user.batch_cap is True

    def test_disables_batch_cap(self, db, auth_client):
        client, user = auth_client
        client.post('/users', data={})  # batch_cap absent → 'on' not present
        db.session.expire(user)
        assert user.batch_cap is False

    def test_invalid_input_redirects_without_error(self, db, auth_client):
        client, user = auth_client
        original = (user.sell_orders_filtering or {}).get('min_margin_percent', 20)
        resp = client.post('/users', data={'min_margin_percent': 'not_a_number'})
        assert resp.status_code == 302
        db.session.expire(user)
        assert user.sell_orders_filtering['min_margin_percent'] == original

    def test_amount_with_spaces_accepted(self, db, auth_client):
        client, user = auth_client
        client.post('/users', data={'min_batch_margin_amount': '10 000 000'})
        db.session.expire(user)
        assert user.sell_orders_filtering['min_batch_margin_amount'] == 10_000_000
