#!/usr/bin/env python3
"""Daily process: download market history, update costs and price advices."""
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
    from process.update_prices import (
        update_market_histories, update_weekly_price_details, update_prices_advices_immediate
    )
    from process.update_costs import update_all_costs

    def _step(label, fn):
        logger.info('--- %s', label)
        t0 = time.time()
        fn()
        logger.info('    done in %.1fs', time.time() - t0)

    t_start = time.time()
    logger.info('=== Daily process started ===')

    _step('Downloading market history', lambda: DownloadHistory(essentials=args.essentials).download())
    _step('Updating market history groups', update_market_histories)
    _step('Updating weekly price details', update_weekly_price_details)
    _step('Updating costs', update_all_costs)
    _step('Updating price advices', update_prices_advices_immediate)

    LastUpdate.set('daily')

    logger.info('=== Daily process finished in %.1fs ===', time.time() - t_start)
