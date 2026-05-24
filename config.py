import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_config():
    path = os.path.join(BASE_DIR, 'config', 'config.json')
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"config/config.json not found at {path}. "
            "Copy config/config.json.example and fill in your credentials."
        )
    with open(path) as f:
        return json.load(f)


_cfg = _load_config()


def _build_database_uri():
    db = _cfg.get('database', {})
    host = db.get('host')
    if host:
        user = db.get('user', '')
        password = db.get('password', '')
        port = db.get('port', 5432)
        name = db.get('name', '')
        return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"
    return f"sqlite:///{os.path.join(BASE_DIR, 'evebs.db')}"


class Config:
    SECRET_KEY = _cfg.get('secret_key', 'dev-secret-change-in-production')
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ESI_CLIENT_ID = _cfg['esi']['client_id']
    ESI_SECRET_KEY = _cfg['esi']['secret_key']

    EVE_SSO_AUTH_URL = 'https://login.eveonline.com/v2/oauth/authorize'
    EVE_SSO_TOKEN_URL = 'https://login.eveonline.com/v2/oauth/token'
    EVE_SSO_VERIFY_URL = 'https://esi.evetech.net/verify/'
    EVE_SSO_SCOPES = ' '.join([
        'esi-characters.read_orders.v1',
        'esi-assets.read_assets.v1',
        'esi-characters.read_blueprints.v1',
        'esi-industry.read_character_jobs.v1',
    ])

    PER_PAGE = 12
    VERBOSE_OUTPUT = _cfg.get('verbose_output', False)
