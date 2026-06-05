#!/usr/bin/env python3
"""Daemon: continuously refresh public market orders.

Trade-hub regions are downloaded every pass. All regions (including non-hub)
are downloaded every 4th pass. Each pass runs the standard price updates.
If a pass finishes in under 15 minutes the daemon sleeps for the remainder.
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
from config import setup_logging, set_logger
setup_logging()
logger = set_logger('downloads')

from app import app

MIN_LOOP_SECONDS = 60*15  # 15 minutes
NON_HUB_EVERY = 4 # Every hour


def _step(label, fn):
    t = time.perf_counter()
    fn()
    logger.info('  %s: %.1fs', label, time.perf_counter() - t)


with app.app_context():
    from esi.download_public_orders.download import download as download_public_orders
    from process.update_jita_market_analytics import update_jita_market_analytics

    step = 0
    while True:
        step += 1
        region_scope = 'hub' if step % NON_HUB_EVERY != 0 else 'all'
        logger.info('=== Orders daemon step %d — regions=%s ===', step, region_scope)
        t_start = time.perf_counter()

        _step('download', lambda: download_public_orders(regions=region_scope))
        _step('jita_market_analytics', update_jita_market_analytics)

        elapsed = time.perf_counter() - t_start
        logger.info('=== Step %d done in %.1fs ===', step, elapsed)

        sleep_for = MIN_LOOP_SECONDS - elapsed
        if sleep_for > 0:
            logger.info('Sleeping %.1fs to reach %dm cadence...', sleep_for, MIN_LOOP_SECONDS // 60)
            time.sleep(sleep_for)
