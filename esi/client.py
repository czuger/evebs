import logging
import os
import json
import time
import base64
from datetime import datetime, timedelta

import requests

from config import Config
from esi import errors as esi_errors
from evebs.extensions import db

logger = logging.getLogger(__name__)

ESI_BASE = 'https://esi.evetech.net/latest/'
EVE_TOKEN_URL = 'https://login.eveonline.com/v2/oauth/token'


class EsiClient:
    def __init__(self, rest_url=None, params=None):
        self.rest_url = rest_url
        self.params = dict(params or {})
        self.params['datasource'] = 'tranquility'
        self._pages_count = 0

    def get_page(self, page_number=None):
        if page_number is not None:
            self.params['page'] = page_number

        url = self._build_url()
        logger.debug('Fetching: %s', url)

        while True:
            try:
                resp = requests.get(url, params=self.params, timeout=30)
                if not resp.ok:
                    error = esi_errors.dispatch(resp.status_code, resp.text)
                    self._print_error(error, url)
                    if error.should_retry():
                        retry_after = resp.headers.get('Retry-After')
                        if retry_after is not None:
                            logger.warning('Retry-After: sleeping %.1fs — %s', float(retry_after), url)
                            time.sleep(float(retry_after))
                        else:
                            error.pause()
                        continue
                    raise error

                remaining = resp.headers.get('X-Ratelimit-Remaining')
                if remaining is not None and int(remaining) < 20:
                    logger.warning('X-Ratelimit-Remaining=%s — sleeping 1s — %s', remaining, url)
                    time.sleep(1)

                self._pages_count = int(resp.headers.get('x-pages', 0))
                try:
                    return resp.json()
                except json.JSONDecodeError:
                    logger.warning('JSON parse error, retrying...')
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
        result = []
        self.params['page'] = 1

        while True:
            logger.debug('Requesting page %s/%s', self.params['page'], self._pages_count)
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
        if not (user.expires_on and user.token and user.renew_token):
            return False

        if user.expires_on < datetime.utcnow():
            self._renew_token(user)

        self.params['token'] = user.token
        return True

    def _renew_token(self, user):
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
            db.session.commit()

    def _build_url(self):
        return ESI_BASE + self.rest_url.lstrip('/')

    def _print_error(self, error, url):
        logger.warning('%s - %s got %s', datetime.utcnow(), url, error)
