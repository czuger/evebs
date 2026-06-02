import logging
from datetime import datetime

from esi.client import EsiClient
from evebs.extensions import db
from evebs.models import BpcAsset, EveItem, UniverseStation, UniverseStructure, UniverseSystem

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

        BpcAsset.query.filter_by(user_id=user.id).update({'touched': False})
        db.session.flush()

        for asset in pages:
            type_id = asset.get('type_id')
            location_id = asset.get('location_id')
            qty = asset.get('quantity', 1)

            eve_item_id = EveItem.to_eve_item_id(type_id)
            if not eve_item_id:
                continue

            station_id = None
            structure_id = None

            if location_id:
                if location_id >= STRUCTURE_ID_MIN:
                    structure_id = self._resolve_structure(location_id, user)
                else:
                    station_id = self._resolve_station(location_id)

            bpc = BpcAsset.query.filter_by(
                user_id=user.id, eve_item_id=eve_item_id
            ).first()
            if bpc:
                bpc.quantity = qty
                bpc.universe_station_id = station_id
                bpc.universe_structure_id = structure_id
                bpc.touched = True
            else:
                bpc = BpcAsset(
                    user_id=user.id, eve_item_id=eve_item_id,
                    quantity=qty, universe_station_id=station_id,
                    universe_structure_id=structure_id, touched=True,
                )
                db.session.add(bpc)

        BpcAsset.query.filter_by(user_id=user.id, touched=False).delete()
        user.download_assets_running = False
        user.last_assets_download = datetime.utcnow()
        db.session.commit()

    def _resolve_structure(self, location_id, user):
        structure = db.session.get(UniverseStructure, location_id)
        if structure:
            return structure.id

        client = EsiClient(f'universe/structures/{location_id}/')
        if not client.set_auth_token(user):
            logger.error('No auth token — cannot fetch structure %s', location_id)
            return None

        try:
            data = client.get_page()
        except Exception as e:
            logger.error('Failed to fetch structure %s: %s', location_id, e)
            return None

        if not data:
            logger.error('Empty response for structure %s', location_id)
            return None

        solar_system_id = data.get('solar_system_id')
        system = UniverseSystem.query.get(solar_system_id) if solar_system_id else None

        structure = UniverseStructure(
            id=location_id,
            name=data.get('name', ''),
            owner_id=data.get('owner_id', 0),
            type_id=data.get('type_id'),
            universe_system_id=system.id if system else None,
        )
        db.session.add(structure)
        db.session.flush()
        return structure.id

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
