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
        resp = client.post('/users', data={'min_pcent_for_advice': 15})
        assert resp.status_code == 302

    def test_updates_numeric_settings(self, db, auth_client):
        client, user = auth_client
        resp = client.post('/users', data={
            'min_pcent_for_advice': '25',
            'min_amount_for_advice': '10000000',
            'vol_month_pcent': '8',
            'batch_cap_multiplier': '5',
        })
        assert resp.status_code == 302

        db.session.expire(user)
        assert user.min_pcent_for_advice == 25
        assert user.min_amount_for_advice == 10_000_000
        assert user.vol_month_pcent == 8
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
        original = user.min_pcent_for_advice
        resp = client.post('/users', data={'min_pcent_for_advice': 'not_a_number'})
        assert resp.status_code == 302
        db.session.expire(user)
        assert user.min_pcent_for_advice == original

    def test_amount_with_spaces_accepted(self, db, auth_client):
        client, user = auth_client
        client.post('/users', data={'min_amount_for_advice': '10 000 000'})
        db.session.expire(user)
        assert user.min_amount_for_advice == 10_000_000
