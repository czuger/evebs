#!/usr/bin/env python3
"""Daily process: download market history, update costs and price advices."""
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

parser = argparse.ArgumentParser(description='Daily ESI download and price update.')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output.')
parser.add_argument('-e', '--essentials', action='store_true',
                    help='Only download TradeHub regions and ammunition/charges items.')
args = parser.parse_args()

from app import app

with app.app_context():
    from evebs.models import LastUpdate

    print('=== Daily process started ===')

    from esi.download_history import DownloadHistory
    from process.update_prices import (
        update_market_histories, update_weekly_price_details, update_prices_advices_immediate
    )
    from process.update_costs import update_all_costs

    DownloadHistory(verbose=args.verbose, essentials=args.essentials).download()
    update_market_histories()
    update_weekly_price_details()
    update_all_costs()
    update_prices_advices_immediate()

    LastUpdate.set('daily')

    print('=== Daily process finished ===')
