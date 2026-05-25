#!/usr/bin/env python3
"""Weekly process: refresh universe data, blueprints, eve items."""
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

parser = argparse.ArgumentParser(description='Weekly ESI universe data refresh.')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output.')
args = parser.parse_args()

from app import app

with app.app_context():
    from evebs.models import LastUpdate

    print('=== Weekly process started ===')

    from esi.download_universe_regions import DownloadUniverseRegions

    DownloadUniverseRegions().download()

    # Blueprint and eve item downloads are data-heavy; see esi/ for individual downloaders
    # Run them manually or via scripts/weekly.sh

    LastUpdate.set('weekly')

    print('=== Weekly process finished ===')
