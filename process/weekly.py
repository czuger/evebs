#!/usr/bin/env python3
"""Weekly process: refresh universe data, blueprints, eve items."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run import app

with app.app_context():
    from evebs.models import LastUpdate

    print('=== Weekly process started ===')

    from esi.download_universe import download_universe

    download_universe()

    # Blueprint and eve item downloads are data-heavy; see esi/ for individual downloaders
    # Run them manually or via scripts/weekly.sh

    LastUpdate.set('weekly')

    print('=== Weekly process finished ===')
