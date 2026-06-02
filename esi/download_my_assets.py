import logging
import random
import string
from datetime import datetime

from esi.client import EsiClient
from evebs.extensions import db
from evebs.models import BpcAsset, EveItem, UniverseStation, UniverseStructure, UnknownStructure


def _random_name():
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    digits  = ''.join(random.choices(string.digits, k=3))
    return f'{letters}-{digits}'


def _resolve_root_location(asset, index_by_id):
    """Walk up the item-in-container chain until we reach a station or structure."""
    seen = set()
    while asset.get('location_type') == 'item':
        parent_id = asset.get('location_id')
        if parent_id in seen or parent_id not in index_by_id:
            break
        seen.add(parent_id)
        asset = index_by_id[parent_id]
    return asset

logger = logging.getLogger(__name__)

STRUCTURE_ID_MIN = 1_000_000_000_000  # NPC stations ~60M, player structures 1T+


class DownloadMyAssets:
    def update(self, user):
        if user.locked:
            logger.debug('%s is locked. Skipping.', user.name)
            return

        client = EsiClient(f'characters/{user.uid}/assets/')
        if not client.set_auth_token(user):
            return

        pages = client.get_all_pages()
        index_by_id = {a['item_id']: a for a in pages if 'item_id' in a}

        BpcAsset.query.filter_by(user_id=user.id).update({'touched': False})
        db.session.flush()

        for asset in pages:
            type_id = asset.get('type_id')
            qty = asset.get('quantity', 1)
            location_flag = asset.get('location_flag')
            location_type = asset.get('location_type')

            eve_item_id = EveItem.to_eve_item_id(type_id)
            if not eve_item_id:
                continue

            root = _resolve_root_location(asset, index_by_id)
            location_id = root.get('location_id')

            station_id = None
            structure_id = None

            if location_id:
                if location_id >= STRUCTURE_ID_MIN:
                    structure_id = self._resolve_structure(location_id)
                else:
                    station_id = self._resolve_station(location_id)

            bpc = BpcAsset.query.filter_by(
                user_id=user.id, eve_item_id=eve_item_id
            ).first()
            if bpc:
                bpc.quantity = qty
                bpc.universe_station_id = station_id
                bpc.universe_structure_id = structure_id
                bpc.location_flag = location_flag
                bpc.location_type = location_type
                bpc.touched = True
            else:
                bpc = BpcAsset(
                    user_id=user.id, eve_item_id=eve_item_id,
                    quantity=qty, universe_station_id=station_id,
                    universe_structure_id=structure_id,
                    location_flag=location_flag, location_type=location_type,
                    touched=True,
                )
                db.session.add(bpc)

        BpcAsset.query.filter_by(user_id=user.id, touched=False).delete()
        user.download_assets_running = False
        user.last_assets_download = datetime.utcnow()
        db.session.commit()

    def _resolve_structure(self, location_id):
        if db.session.get(UniverseStructure, location_id):
            return location_id
        if not db.session.get(UnknownStructure, location_id):
            db.session.add(UnknownStructure(id=location_id, name=_random_name()))
            db.session.flush()
            logger.debug('Created UnknownStructure %s — run DownloadUniverseStructures to resolve it', location_id)
        return location_id

    def _resolve_station(self, location_id):
        station = db.session.get(UniverseStation, location_id)
        if station:
            return station.id

        client = EsiClient(f'universe/stations/{location_id}/')
        try:
            data = client.get_page()
        except Exception as e:
            logger.error('Failed to fetch station %s: %s', location_id, e)
            return None

        if not data:
            logger.error('Station %s not found in ESI', location_id)
            return None

        station = UniverseStation(
            id=location_id,
            name=data.get('name', ''),
            office_rental_cost=data.get('office_rental_cost', 0.0),
            universe_system_id=data.get('system_id'),
        )
        db.session.add(station)
        db.session.flush()
        return station.id
