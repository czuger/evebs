import os
import json
import time
import base64
from datetime import datetime, timedelta

import requests

from esi import errors as esi_errors

ESI_BASE = 'https://esi.evetech.net/latest/'
EVE_TOKEN_URL = 'https://login.eveonline.com/v2/oauth/token'


class EsiClient:
    """HTTP client for the EVE ESI API with pagination, retries, and rate-limit handling."""

    def __init__(self, rest_url=None, params=None, debug=False, verbose=False):
        self.rest_url = rest_url
        self.params = dict(params or {})
        self.params['datasource'] = 'tranquility'
        self.debug = debug
        self.verbose = verbose or (os.environ.get('EBS_VERBOSE_OUTPUT', '').lower() == 'true')
        self._pages_count = 0

    def get_page(self, page_number=None):
        """Fetch a single page from the ESI endpoint, retrying on transient errors."""
        if page_number is not None:
            self.params['page'] = page_number

        url = self._build_url()
        if self.debug:
            print(f'Fetching: {url}')

        while True:
            try:
                resp = requests.get(url, params=self.params, timeout=30)

                if resp.status_code == 429:
                    retry_after = resp.headers.get('Retry-After', 60)
                    error = esi_errors.RateLimited(f'HTTP 429: rate limited', retry_after=retry_after)
                    self._print_error(error, url)
                    error.pause()
                    continue

                if not resp.ok:
                    error = esi_errors.dispatch(resp.status_code, resp.text)
                    self._print_error(error, url)
                    if error.should_retry():
                        error.pause()
                        continue
                    raise error

                self._pages_count = int(resp.headers.get('x-pages', 0))
                self._backoff_if_needed(resp.headers)
                try:
                    return resp.json()
                except json.JSONDecodeError:
                    print('JSON parse error, retrying...')
                    continue

            except requests.exceptions.Timeout:
                error = esi_errors.OpenTimeout('timeout')
                error.pause()
                continue
            except requests.exceptions.ConnectionError:
                error = esi_errors.SocketError('connection error')
                error.pause()
                continue

    def get_all_pages(self):
        """Fetch all pages and return their combined results as a list."""
        result = []
        self.params['page'] = 1

        while True:
            if self.debug:
                print(f'Requesting page {self.params["page"]}/{self._pages_count}')
            page_data = self.get_page()
            if isinstance(page_data, list):
                result.extend(page_data)
            elif isinstance(page_data, dict):
                result.append(page_data)

            if self._pages_count <= 1:
                break
            self.params['page'] += 1
            if self.params['page'] > self._pages_count:
                self.params.pop('page', None)
                break

        return result

    def set_auth_token(self, user):
        """Attach the user's bearer token to subsequent requests, refreshing if expired."""
        if not (user.expires_on and user.token and user.renew_token):
            return False

        if user.expires_on < datetime.utcnow():
            self._renew_token(user)

        self.params['token'] = user.token
        return True

    def _renew_token(self, user):
        """Exchange the user's refresh token for a new access token."""
        from config import Config
        client_id = Config.ESI_CLIENT_ID
        secret_key = Config.ESI_SECRET_KEY
        auth = base64.b64encode(f'{client_id}:{secret_key}'.encode()).decode()
        resp = requests.post(EVE_TOKEN_URL, data={
            'grant_type': 'refresh_token',
            'refresh_token': user.renew_token,
        }, headers={'Authorization': f'Basic {auth}',
                    'Content-Type': 'application/x-www-form-urlencoded'})
        if resp.ok:
            data = resp.json()
            user.token = data['access_token']
            user.expires_on = datetime.utcnow() + timedelta(seconds=data.get('expires_in', 1200))
            from evebs.extensions import db
            db.session.commit()

    def _backoff_if_needed(self, headers):
        """Slow down requests when the ESI rate-limit budget is nearly exhausted."""
        remaining = headers.get('X-Ratelimit-Remaining')
        if remaining is None:
            return
        remaining = int(remaining)
        if remaining < 5:
            time.sleep(2)
        elif remaining < 15:
            time.sleep(0.5)

    def _build_url(self):
        """Construct the full ESI URL by joining the base with the relative path."""
        return ESI_BASE + self.rest_url.lstrip('/')

    def _print_error(self, error, url):
        """Log the error with a timestamp and the failing URL."""
        print(f'{datetime.utcnow()} - {url} got {error}', flush=True)
