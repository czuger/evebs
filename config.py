import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_config():
    path = os.path.join(BASE_DIR, 'config', 'config.json')
    with open(path) as f:
        return json.load(f)


_cfg = _load_config()
_db = _cfg['database']


class Config:
    SECRET_KEY = _cfg.get('secret_key', 'dev-secret-change-in-production')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or (
        f"postgresql+psycopg://{_db['user']}:{_db['password']}"
        f"@{_db['host']}:{_db['port']}/{_db['name']}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ESI_CLIENT_ID = _cfg['esi']['client_id']
    ESI_SECRET_KEY = _cfg['esi']['secret_key']

    EVE_SSO_AUTH_URL = 'https://login.eveonline.com/v2/oauth/authorize'
    EVE_SSO_TOKEN_URL = 'https://login.eveonline.com/v2/oauth/token'
    EVE_SSO_VERIFY_URL = 'https://esi.evetech.net/verify/'
    EVE_SSO_SCOPES = ' '.join([
        'esi-markets.read_character_orders.v1',
        'esi-assets.read_assets.v1',
        'esi-characters.read_blueprints.v1',
        # 'esi-industry.read_character_jobs.v1',
    ])

    PER_PAGE = 12
    VERBOSE_OUTPUT = False


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg://{_db['user']}:{_db['password']}"
        f"@{_db['host']}:{_db['port']}/{_db['name']}_test"
    )
