import os
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_omniauth():
    path = os.path.join(BASE_DIR, 'config', 'omniauth.yaml')
    if os.path.exists(path):
        with open(path) as f:
            data = yaml.safe_load(f)
        if data and 'esi' in data:
            return data['esi']
    return [None, None]


_esi_creds = _load_omniauth()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "evebs.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ESI_CLIENT_ID = os.environ.get('ESI_CLIENT_ID', _esi_creds[0])
    ESI_SECRET_KEY = os.environ.get('ESI_SECRET_KEY', _esi_creds[1])

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
    VERBOSE_OUTPUT = os.environ.get('EBS_VERBOSE_OUTPUT', 'false').lower() == 'true'
