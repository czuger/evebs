"""Tests for esi/client.py — HTTP mocked, no real ESI calls."""
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from esi.client import EsiClient
from esi.errors import Forbidden, NotFound, ServiceUnavailable


# ---------------------------------------------------------------------------
# get_page
# ---------------------------------------------------------------------------

def _mock_resp(data, pages=1, ok=True, status=200, text=''):
    r = MagicMock()
    r.ok = ok
    r.status_code = status
    r.text = text
    r.headers = {'x-pages': str(pages)}
    r.json.return_value = data
    return r


class TestGetPage:
    def test_returns_parsed_json(self):
        resp = _mock_resp([{'type_id': 34, 'adjusted_price': 5.0}])
        with patch('esi.client.requests.get', return_value=resp):
            result = EsiClient('markets/prices/').get_page()
        assert result == [{'type_id': 34, 'adjusted_price': 5.0}]

    def test_stores_pages_count(self):
        resp = _mock_resp([], pages=7)
        with patch('esi.client.requests.get', return_value=resp):
            client = EsiClient('markets/prices/')
            client.get_page()
        assert client._pages_count == 7

    def test_raises_forbidden_without_retry(self):
        resp = _mock_resp(None, ok=False, status=403, text='Forbidden')
        with patch('esi.client.requests.get', return_value=resp):
            with pytest.raises(Forbidden):
                EsiClient('characters/1/orders/').get_page()

    def test_raises_not_found_without_retry(self):
        resp = _mock_resp(None, ok=False, status=404, text='Not Found')
        with patch('esi.client.requests.get', return_value=resp):
            with pytest.raises(NotFound):
                EsiClient('markets/10000002/orders/').get_page()

    def test_retries_on_503_then_succeeds(self):
        bad = _mock_resp(None, ok=False, status=503, text='Service Unavailable')
        good = _mock_resp([{'id': 1}])
        with patch('esi.client.requests.get', side_effect=[bad, good]):
            with patch('esi.errors.ServiceUnavailable.pause'):
                result = EsiClient('markets/prices/').get_page()
        assert result == [{'id': 1}]

    def test_retries_on_json_decode_error(self):
        bad = MagicMock()
        bad.ok = True
        bad.headers = {'x-pages': '1'}
        bad.json.side_effect = json.JSONDecodeError('err', '', 0)

        good = _mock_resp([{'id': 2}])

        with patch('esi.client.requests.get', side_effect=[bad, good]):
            result = EsiClient('markets/prices/').get_page()
        assert result == [{'id': 2}]

    def test_injects_datasource_param(self):
        resp = _mock_resp([])
        with patch('esi.client.requests.get', return_value=resp) as mock_get:
            EsiClient('markets/prices/').get_page()
        _, kwargs = mock_get.call_args
        assert kwargs['params']['datasource'] == 'tranquility'


# ---------------------------------------------------------------------------
# get_all_pages
# ---------------------------------------------------------------------------

class TestGetAllPages:
    def test_single_page_list_response(self):
        resp = _mock_resp([{'id': 1}, {'id': 2}], pages=1)
        with patch('esi.client.requests.get', return_value=resp):
            result = EsiClient('markets/prices/').get_all_pages()
        assert result == [{'id': 1}, {'id': 2}]

    def test_multi_page_list_response(self):
        resps = [
            _mock_resp([{'id': i}], pages=3)
            for i in range(1, 4)
        ]
        with patch('esi.client.requests.get', side_effect=resps):
            result = EsiClient('markets/10000002/orders/').get_all_pages()
        assert [r['id'] for r in result] == [1, 2, 3]

    def test_dict_response_is_wrapped_in_list(self):
        resp = _mock_resp({'name': 'Jita', 'region_id': 10000002}, pages=1)
        with patch('esi.client.requests.get', return_value=resp):
            result = EsiClient('universe/systems/30000142/').get_all_pages()
        assert result == [{'name': 'Jita', 'region_id': 10000002}]

    def test_empty_response(self):
        resp = _mock_resp([], pages=1)
        with patch('esi.client.requests.get', return_value=resp):
            result = EsiClient('characters/1/orders/').get_all_pages()
        assert result == []


# ---------------------------------------------------------------------------
# set_auth_token
# ---------------------------------------------------------------------------

class TestSetAuthToken:
    def test_returns_false_when_token_missing(self):
        from evebs.models import User
        u = User(uid='1', name='x', provider='p', token=None, renew_token=None, expires_on=None)
        assert EsiClient('x/').set_auth_token(u) is False

    def test_returns_false_when_renew_token_missing(self):
        from evebs.models import User
        u = User(uid='1', name='x', provider='p',
                 token='t', renew_token=None,
                 expires_on=datetime.utcnow() + timedelta(hours=1))
        assert EsiClient('x/').set_auth_token(u) is False

    def test_sets_token_param_for_valid_unexpired_user(self, db, user):
        client = EsiClient('characters/123/orders/')
        result = client.set_auth_token(user)
        assert result is True
        assert client.params['token'] == 'tok_test'

    def test_renews_expired_token_and_persists(self, db, user):
        user.expires_on = datetime.utcnow() - timedelta(seconds=10)
        db.session.commit()

        new_resp = MagicMock()
        new_resp.ok = True
        new_resp.json.return_value = {'access_token': 'new_tok', 'expires_in': 1200}

        with patch('esi.client.requests.post', return_value=new_resp):
            client = EsiClient('characters/123/orders/')
            result = client.set_auth_token(user)

        assert result is True
        db.session.expire(user)
        assert user.token == 'new_tok'
