#!/usr/bin/env python3
"""Hourly process: download public orders + market prices, update analytics."""
import argparse
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
from config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Hourly ESI download and price update.')
parser.add_argument('-e', '--essentials', action='store_true',
                    help='Only download TradeHub regions and ammunition/charges items.')
parser.add_argument('-n', '--no-download', action='store_true',
                    help='Skip ESI downloads and reuse existing data files.')
args = parser.parse_args()

from app import app

with app.app_context():
    from evebs.models import Crontab, LastUpdate

    Crontab.stop('hourly')
    Crontab.start('hourly')

    from esi.download_public_orders import download as download_public_orders
    from esi.download_markets_prices import DownloadMarketsPrices
    from process.update_prices import update_buy_orders_analytics

    def _step(label, fn):
        logger.info('--- %s', label)
        t0 = time.time()
        fn()
        logger.info('    done in %.1fs', time.time() - t0)

    t_start = time.time()
    logger.info('=== Hourly process started ===')

    if args.no_download:
        logger.info('Skipping downloads (--no-download).')
    else:
        _step('Downloading public trade orders',
              lambda: download_public_orders(essentials=args.essentials))
        _step('Downloading market prices', DownloadMarketsPrices().download)

    _step('Updating buy orders analytics', update_buy_orders_analytics)

    LastUpdate.set('hourly')
    Crontab.stop('hourly')

    logger.info('=== Hourly process finished in %.1fs ===', time.time() - t_start)
