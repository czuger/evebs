"""Tests for evebs/routes/auth.py."""
import base64
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from evebs.routes.auth import _jwt_payload


# ---------------------------------------------------------------------------
# _jwt_payload helper
# ---------------------------------------------------------------------------

def _make_jwt(char_id=123456789, char_name='Test Pilot'):
    header = base64.urlsafe_b64encode(b'{"alg":"RS256"}').decode().rstrip('=')
    payload = base64.urlsafe_b64encode(
        json.dumps({'sub': f'CHARACTER:EVE:{char_id}', 'name': char_name}).encode()
    ).decode().rstrip('=')
    return f'{header}.{payload}.fakesig'


class TestJwtPayload:
    def test_decodes_sub_and_name(self):
        tok = _make_jwt(char_id=999, char_name='Alpha')
        claims = _jwt_payload(tok)
        assert claims['sub'] == 'CHARACTER:EVE:999'
        assert claims['name'] == 'Alpha'

    def test_handles_missing_padding(self):
        # Payload length not a multiple of 4 — padding must be added
        payload = base64.urlsafe_b64encode(b'{"sub":"CHARACTER:EVE:1","name":"x"}').decode().rstrip('=')
        tok = f'header.{payload}.sig'
        claims = _jwt_payload(tok)
        assert claims['sub'] == 'CHARACTER:EVE:1'


# ---------------------------------------------------------------------------
# /auth/eve_online_sso/callback
# ---------------------------------------------------------------------------

class TestCallback:
    def _token_resp(self, char_id=123456789, char_name='Test Pilot'):
        jwt = _make_jwt(char_id, char_name)
        r = MagicMock()
        r.ok = True
        r.json.return_value = {
            'access_token': jwt,
            'refresh_token': 'ref_tok',
            'expires_in': 1200,
        }
        return r

    def test_missing_code_redirects_to_index(self, client):
        resp = client.get('/auth/eve_online_sso/callback')
        assert resp.status_code == 302
        assert '/' in resp.location

    def test_creates_new_user_on_first_login(self, db, client):
        with patch('evebs.routes.auth.requests.post', return_value=self._token_resp(char_id=55555)):
            resp = client.get('/auth/eve_online_sso/callback?code=testcode')

        from evebs.models import User
        u = User.query.filter_by(uid='55555').first()
        assert u is not None
        assert u.name == 'Test Pilot'
        assert resp.status_code == 302

    def test_updates_existing_user_token(self, db, user, client):
        with patch('evebs.routes.auth.requests.post',
                   return_value=self._token_resp(char_id=123456789, char_name='Renamed')):
            client.get('/auth/eve_online_sso/callback?code=testcode')

        db.session.expire(user)
        assert user.name == 'Renamed'

    def test_failed_token_exchange_redirects(self, db, client):
        r = MagicMock()
        r.ok = False
        with patch('evebs.routes.auth.requests.post', return_value=r):
            resp = client.get('/auth/eve_online_sso/callback?code=bad')
        assert resp.status_code == 302

    def test_signout_logs_out_and_redirects(self, auth_client):
        client, _ = auth_client
        resp = client.get('/signout')
        assert resp.status_code == 302
        # Session should no longer carry user_id
        with client.session_transaction() as sess:
            assert '_user_id' not in sess
