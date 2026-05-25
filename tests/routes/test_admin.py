"""Tests for evebs/routes/admin.py."""
import pytest


class TestAdminShow:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/admin_tools')
        assert resp.status_code == 302

    def test_redirects_non_admin_to_denied(self, auth_client):
        client, _ = auth_client
        resp = client.get('/admin_tools')
        assert resp.status_code == 302
        assert 'denied' in resp.location

    def test_returns_200_for_admin(self, admin_client):
        client, _ = admin_client
        resp = client.get('/admin_tools')
        assert resp.status_code == 200

    def test_shows_last_update_entries(self, db, admin_client):
        from evebs.models import LastUpdate
        LastUpdate.set('hourly')
        LastUpdate.set('daily')
        db.session.commit()

        client, _ = admin_client
        resp = client.get('/admin_tools')
        assert resp.status_code == 200


class TestAdminDenied:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/admin_tools/denied')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        resp = client.get('/admin_tools/denied')
        assert resp.status_code == 200


class TestAdminActivity:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/admin_tools/activity')
        assert resp.status_code == 302

    def test_redirects_non_admin_to_denied(self, auth_client):
        client, _ = auth_client
        resp = client.get('/admin_tools/activity')
        assert resp.status_code == 302
        assert 'denied' in resp.location

    def test_returns_200_for_admin(self, admin_client):
        client, _ = admin_client
        resp = client.get('/admin_tools/activity')
        assert resp.status_code == 200

    def test_shows_activity_log_entries(self, db, admin_client):
        from evebs.models import UserActivityLog
        log = UserActivityLog(ip='127.0.0.1', action='login', user='Test Pilot')
        db.session.add(log)
        db.session.commit()

        client, _ = admin_client
        resp = client.get('/admin_tools/activity')
        assert resp.status_code == 200
        assert b'127.0.0.1' in resp.data
