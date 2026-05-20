#!/usr/bin/env python3
"""Hourly process: download market orders, refresh price views, update analytics."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run import app

with app.app_context():
    from evebs.models import Crontab, LastUpdate

    Crontab.start('hourly')

    print('=== Hourly process started ===')

    from esi.download_region_orders import download_region_orders
    from process.update_prices import (
        update_buy_orders_analytics, update_prices_advices_immediate
    )

    download_region_orders()
    update_prices_advices_immediate()
    update_buy_orders_analytics()

    LastUpdate.set('hourly')
    Crontab.stop('hourly')

    print('=== Hourly process finished ===')
