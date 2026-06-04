#!/usr/bin/env python3
"""Daily process: placeholder — weekly price details have been removed."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
from config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

from app import app

with app.app_context():
    from evebs.models import LastUpdate
    LastUpdate.set('daily')
    logger.info('Daily process: nothing to do.')
