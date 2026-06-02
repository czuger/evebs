#!/usr/bin/env python3
"""Weekly process: refresh universe data, blueprints, eve items."""
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
from config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Weekly ESI universe data refresh.')
args = parser.parse_args()

from app import app

with app.app_context():
    from evebs.models import LastUpdate

    logger.info('=== Weekly process started ===')

    from esi.download_universe_regions import DownloadUniverseRegions
    from esi.download_universe_structures import DownloadUniverseStructures
    from esi.download_universe_stations import DownloadUniverseStations

    DownloadUniverseRegions().download()
    DownloadUniverseStations().download()
    DownloadUniverseStructures().download()

    # Blueprint and eve item downloads are data-heavy; see esi/ for individual downloaders
    # Run them manually or via scripts/weekly.sh

    LastUpdate.set('weekly')

    logger.info('=== Weekly process finished ===')
