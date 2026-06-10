"""Download all known public structures from the EveRef bulk dataset."""
import logging
import os
import sys

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from config import setup_logging
from evebs.extensions import db
from evebs.models import UniverseStructure, UniverseSystem

logger = logging.getLogger(__name__)

EVEREF_STRUCTURES_URL = 'https://data.everef.net/structures/structures-latest.v2.json'


class DownloadUniverseStructures:
    def download(self):
        logger.info('Fetching structures from EveRef…')
        resp = requests.get(EVEREF_STRUCTURES_URL, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        logger.info('Downloaded %d structure records', len(data))

        valid_system_ids = {row.id for row in UniverseSystem.query.with_entities(UniverseSystem.id).all()}
        logger.debug('%d known solar systems loaded', len(valid_system_ids))

        new = updated = skipped = 0
        batch = 0

        for key, rec in data.items():
            structure_id = rec.get('structure_id') or int(key)
            name = rec.get('name', '')
            owner_id = rec.get('owner_id')
            type_id = rec.get('type_id')
            solar_system_id = rec.get('solar_system_id')

            if not owner_id:
                skipped += 1
                continue

            system_id = solar_system_id if solar_system_id in valid_system_ids else None

            existing = db.session.get(UniverseStructure, structure_id)
            if existing:
                existing.name = name
                existing.owner_id = owner_id
                existing.type_id = type_id
                existing.universe_system_id = system_id
                updated += 1
            else:
                db.session.add(UniverseStructure(
                    id=structure_id,
                    name=name,
                    owner_id=owner_id,
                    type_id=type_id,
                    universe_system_id=system_id,
                ))
                new += 1

            batch += 1
            if batch % 2000 == 0:
                db.session.flush()

        db.session.commit()
        logger.info('Structures: %d new, %d updated, %d skipped (no owner_id)', new, updated, skipped)


if __name__ == '__main__':
    setup_logging()
    with app.app_context():
        DownloadUniverseStructures().download()
