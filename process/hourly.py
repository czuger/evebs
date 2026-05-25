#!/usr/bin/env python3
"""Hourly process: download public orders + market prices, update analytics."""
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

parser = argparse.ArgumentParser(description='Hourly ESI download and price update.')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output.')
args = parser.parse_args()

from app import app

with app.app_context():
    from evebs.models import Crontab, LastUpdate

    Crontab.start('hourly')

    print('=== Hourly process started ===')

    from esi.download_public_orders import DownloadPublicTradesOrders
    from esi.download_markets_prices import DownloadMarketsPrices
    from process.update_public_orders import run as update_orders
    from process.update_prices import (
        update_prices_min, update_buy_orders_analytics, update_prices_advices_immediate
    )

    DownloadPublicTradesOrders(verbose=args.verbose).download()
    DownloadMarketsPrices().download()

    update_orders(verbose=args.verbose)
    update_prices_min()
    update_prices_advices_immediate()
    update_buy_orders_analytics()

    LastUpdate.set('hourly')
    Crontab.stop('hourly')

    print('=== Hourly process finished ===')
