import json
import logging
import logging.handlers
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_config():
    env      = os.getenv('FLASK_ENV', 'development')
    filename = 'production_config.json' if env == 'production' else 'dev_config.json'
    path     = os.path.join(BASE_DIR, 'config', filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"config/{filename} not found. "
            f"Copy config/{filename}.example and fill in your credentials."
        )
    with open(path) as f:
        return json.load(f)


_cfg = _load_config()


_test_mode = os.getenv('EVEBS_TEST_DB', '').lower() in ('1', 'true', 'yes')


def _build_database_uri():
    db = _cfg.get('database', {})
    host = db.get('host')
    if host:
        user = db.get('user', '')
        password = db.get('password', '')
        port = db.get('port', 5432)
        name = db.get('name', '')
        if _test_mode:
            name = f'{name}_test'
        return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"
    base = os.path.join(BASE_DIR, 'evebs_test.db' if _test_mode else 'evebs.db')
    return f"sqlite:///{base}"


class Config:
    SECRET_KEY = _cfg.get('secret_key', 'dev-secret-change-in-production')
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SERVER_NAME          = _cfg.get('server_name')        or None
    APPLICATION_ROOT     = _cfg.get('application_root',   '/')
    PREFERRED_URL_SCHEME = _cfg.get('preferred_url_scheme', 'http')

    ESI_CLIENT_ID = _cfg['esi']['client_id']
    ESI_SECRET_KEY = _cfg['esi']['secret_key']

    EVE_SSO_AUTH_URL = 'https://login.eveonline.com/v2/oauth/authorize'
    EVE_SSO_TOKEN_URL = 'https://login.eveonline.com/v2/oauth/token'
    EVE_SSO_VERIFY_URL = 'https://esi.evetech.net/verify/'
    EVE_SSO_SCOPES = ' '.join([
        "esi-location.read_location.v1", "esi-industry.read_character_jobs.v1",
        "esi-assets.read_corporation_assets.v1", "publicData", "esi-universe.read_structures.v1",
        "esi-assets.read_assets.v1", "esi-markets.structure_markets.v1", "esi-markets.read_character_orders.v1",
        "esi-characters.read_blueprints.v1"
    ])

    PER_PAGE = 12
    VERBOSE_OUTPUT = _cfg.get('verbose_output', False)
    REDIS_URL = _cfg['redis_url']


def setup_logging(level=logging.DEBUG):
    from pythonjsonlogger import jsonlogger

    log_dir = os.path.join(BASE_DIR, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'evebs.log'),
        when='midnight',
        backupCount=30,
        encoding='utf-8',
    )
    file_handler.suffix = '%Y-%m-%d'
    file_handler.setFormatter(jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%SZ',
    ))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    ))

    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    logging.getLogger('esi.client').setLevel(logging.WARNING)

    root.addHandler(file_handler)
    root.addHandler(console_handler)
