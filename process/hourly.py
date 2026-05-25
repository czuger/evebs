#!/usr/bin/env python3
"""Hourly process: download public orders + market prices, update analytics."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

    verbose = os.environ.get('EBS_VERBOSE_OUTPUT', 'false').lower() == 'true'

    DownloadPublicTradesOrders(verbose=verbose).download()
    DownloadMarketsPrices().download()

    update_orders(verbose=verbose)
    update_prices_min()
    update_prices_advices_immediate()
    update_buy_orders_analytics()

    LastUpdate.set('hourly')
    Crontab.stop('hourly')

    print('=== Hourly process finished ===')
