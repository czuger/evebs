"""Tests for evebs/routes/price_advices.py."""
import pytest


class TestAdvicePrices:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/price_advices/advice_prices')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        resp = client.get('/price_advices/advice_prices')
        assert resp.status_code == 200


class TestAdvicePricesWeekly:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/price_advices/advice_prices_weekly')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        resp = client.get('/price_advices/advice_prices_weekly')
        assert resp.status_code == 200


class TestEmptyPlaces:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/price_advices/empty_places')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client, db):
        client, _ = auth_client
        resp = client.get('/price_advices/empty_places')
        assert resp.status_code == 200

    def test_pagination_accepted(self, auth_client, db):
        client, _ = auth_client
        resp = client.get('/price_advices/empty_places?page=1')
        assert resp.status_code == 200
