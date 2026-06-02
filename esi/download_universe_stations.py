"""Fetch station names and details from ESI for all stations in the DB."""
import argparse
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from esi.client import EsiClient
from esi.errors import NotFound

logger = logging.getLogger(__name__)


class DownloadUniverseStations:
    def download(self, empty_only=True):
        from evebs.extensions import db
        from evebs.models import UniverseStation

        query = UniverseStation.query
        if empty_only:
            query = query.filter(UniverseStation.name == '')

        stations = query.all()
        logger.info('Fetching ESI data for %d stations (empty_only=%s)', len(stations), empty_only)

        updated = errors = 0
        for i, station in enumerate(stations, 1):
            client = EsiClient(f'universe/stations/{station.id}/')
            try:
                data = client.get_page()
            except NotFound:
                logger.warning('Station %s not found in ESI', station.id)
                errors += 1
                continue
            except Exception as e:
                logger.warning('Failed to fetch station %s: %s', station.id, e)
                errors += 1
                continue

            if not data:
                errors += 1
                continue

            station.name = data.get('name', '') or ''
            station.office_rental_cost = data.get('office_rental_cost', 0.0) or 0.0
            station.security_status = data.get('system_security_status')

            updated += 1
            if i % 100 == 0:
                db.session.flush()
                logger.info('  %d / %d done', i, len(stations))

            time.sleep(0.05)

        db.session.commit()
        logger.info('Stations updated: %d, errors: %d', updated, errors)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch station names from ESI.')
    parser.add_argument('-a', '--all', action='store_true',
                        help='Update all stations, not just those with empty names.')
    args = parser.parse_args()

    from config import setup_logging
    setup_logging()
    from app import app
    with app.app_context():
        DownloadUniverseStations().download(empty_only=not args.all)
