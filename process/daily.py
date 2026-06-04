#!/usr/bin/env python3
"""Daily process: download market history, update weekly price details."""
import argparse
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
from config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Daily ESI download and price update.')
parser.add_argument('-e', '--essentials', action='store_true',
                    help='Only download TradeHub regions and ammunition/charges items.')
args = parser.parse_args()

from app import app

with app.app_context():
    from evebs.models import LastUpdate

    from esi.download_history import DownloadHistory
    from process.update_prices import update_weekly_price_details

    def _step(label, fn):
        logger.info('--- %s', label)
        t0 = time.time()
        fn()
        logger.info('    done in %.1fs', time.time() - t0)

    t_start = time.time()
    logger.info('=== Daily process started ===')

    _step('Downloading market history', lambda: DownloadHistory(essentials=args.essentials).download())
    _step('Updating weekly price details', update_weekly_price_details)

    LastUpdate.set('daily')

    logger.info('=== Daily process finished in %.1fs ===', time.time() - t_start)
