#!/usr/bin/env python3
"""Background asset sync for a single user."""
import argparse
import logging
import logging.handlers
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import setup_logging, BASE_DIR

setup_logging()

# Dedicated log file for asset actualisation
_sync_handler = logging.handlers.TimedRotatingFileHandler(
    filename=os.path.join(BASE_DIR, 'logs', 'assets_sync.log'),
    when='midnight',
    backupCount=30,
    encoding='utf-8',
)
_sync_handler.suffix = '%Y-%m-%d'
from pythonjsonlogger import jsonlogger
_sync_handler.setFormatter(jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%SZ',
))
logging.getLogger().addHandler(_sync_handler)

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Sync assets for a user in the background.')
parser.add_argument('-u', '--user-id', type=int, required=True,
                    help='Database ID of the user whose assets to sync.')
args = parser.parse_args()

import redis as redis_lib

from app import app
from esi.download_my_assets import DownloadMyAssets
from evebs.extensions import db
from evebs.models import User

REDIS_KEY = f'assets_sync:{args.user_id}'

with app.app_context():
    r = redis_lib.from_url(app.config['REDIS_URL'])

    user = db.session.get(User, args.user_id)
    if not user:
        logger.error('User %s not found — aborting sync', args.user_id)
        sys.exit(1)

    r.set(REDIS_KEY, 'running', ex=300)
    logger.info('Assets sync started for user %s (%s)', args.user_id, user.name)

    try:
        DownloadMyAssets().update(user)
        r.set(REDIS_KEY, 'done', ex=30)
        logger.info('Assets sync done for user %s (%s)', args.user_id, user.name)
    except Exception as e:
        logger.error('Assets sync failed for user %s: %s', args.user_id, e, exc_info=True)
        r.set(REDIS_KEY, 'error', ex=30)
