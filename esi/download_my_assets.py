import json
import logging
import os
import random
import string
from datetime import datetime

from esi.client import EsiClient
from evebs.extensions import db
from evebs.models import UserAsset, EveItem, UniverseStation, UniverseStructure, UnknownStructure


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

_BLUEPRINTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'eve_static_data', 'blueprints.jsonl')


def _load_blueprint_activities():
    """Return (activities, bp_to_produced).

    activities:     {blueprintTypeID: {can_copy, invention_products: [blueprintTypeID, ...]}}
    bp_to_produced: {blueprintTypeID: produced_type_id}  — from manufacturing.products
    """
    activities = {}
    bp_to_produced = {}
    with open(_BLUEPRINTS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            bp = json.loads(line)
            bp_id = bp.get('_key')
            if bp_id is None:
                continue
            acts = bp.get('activities', {})

            mfg_products = acts.get('manufacturing', {}).get('products', [])
            if mfg_products:
                bp_to_produced[bp_id] = mfg_products[0]['typeID']

            can_copy = 'copying' in acts
            invention_products = [
                p['typeID'] for p in acts.get('invention', {}).get('products', [])
            ]
            if can_copy or invention_products:
                activities[bp_id] = {'can_copy': can_copy, 'invention_products': invention_products}

    return activities, bp_to_produced


_INVENT_PRIORITY = {'invent': 2, 'copy_invent': 1}


def _compute_potentials(real_bpo_ids, real_bpc_ids, activities):
    """Pure BFS over blueprint activities. Returns {eve_item_id: potential_type}.

    Potential types:
    - 'copy':        user has BPO but no BPC; blueprint can be copied
    - 'invent':      can be invented; user already has a BPC (real or itself invented)
    - 'copy_invent': can be invented but user must copy a BPO first
    """
    real_all_ids = real_bpo_ids | real_bpc_ids
    potentials = {}

    queue = [(bp_id, True) for bp_id in real_bpo_ids]
    queue += [(bp_id, False) for bp_id in real_bpc_ids]
    visited = set()

    while queue:
        bp_id, is_bpo = queue.pop()
        key = (bp_id, is_bpo)
        if key in visited:
            continue
        visited.add(key)

        acts = activities.get(bp_id, {})

        if is_bpo and acts.get('can_copy') and bp_id not in real_bpc_ids:
            if bp_id not in potentials:
                potentials[bp_id] = 'copy'
            queue.append((bp_id, False))

        source_has_bpc = (not is_bpo) and (
            bp_id in real_bpc_ids or potentials.get(bp_id) == 'invent'
        )
        new_type = 'invent' if source_has_bpc else 'copy_invent'

        for invented_bp_id in acts.get('invention_products', []):
            if invented_bp_id in real_all_ids:
                continue
            current = potentials.get(invented_bp_id)
            if _INVENT_PRIORITY.get(new_type, 0) > _INVENT_PRIORITY.get(current, 0):
                potentials[invented_bp_id] = new_type
                queue.append((invented_bp_id, True))
                queue.append((invented_bp_id, False))

    return potentials


def _generate_potential_assets(user, activities, bp_to_produced):
    db.session.query(UserAsset).filter_by(user_id=user.id, is_potential=True).delete()

    real = db.session.query(UserAsset).filter_by(user_id=user.id, is_potential=False).all()
    real_bpo_ids = {a.eve_item_id for a in real if not a.is_blueprint_copy}
    real_bpc_ids = {a.eve_item_id for a in real if a.is_blueprint_copy}

    potentials = _compute_potentials(real_bpo_ids, real_bpc_ids, activities)

    inserted = 0
    for blueprint_type_id, potential_type in potentials.items():
        produced_type_id = bp_to_produced.get(blueprint_type_id)
        if produced_type_id is None:
            continue
        db.session.add(UserAsset(
            user_id=user.id,
            eve_item_id=produced_type_id,
            is_blueprint_copy=True,
            is_potential=True,
            potential_type=potential_type,
            quantity=0,
        ))
        inserted += 1

    logger.info('Generated %d potential blueprint entries for user %s', inserted, user.id)


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

        UserAsset.query.filter_by(user_id=user.id).update({'touched': False})
        db.session.flush()

        for asset in pages:
            type_id = asset.get('type_id')
            qty = asset.get('quantity', 1)
            location_flag = asset.get('location_flag')
            location_type = asset.get('location_type')
            esi_item_id = asset.get('item_id')
            is_blueprint_copy = asset.get('is_blueprint_copy', False)
            parent_esi_item_id = (
                asset.get('location_id') if location_type == 'item' else None
            )

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

            bpc = UserAsset.query.filter_by(
                user_id=user.id, esi_item_id=esi_item_id
            ).first()
            if bpc:
                bpc.quantity = qty
                bpc.universe_station_id = station_id
                bpc.universe_structure_id = structure_id
                bpc.location_flag = location_flag
                bpc.location_type = location_type
                bpc.parent_esi_item_id = parent_esi_item_id
                bpc.is_blueprint_copy = is_blueprint_copy
                bpc.touched = True
            else:
                bpc = UserAsset(
                    user_id=user.id, eve_item_id=eve_item_id,
                    esi_item_id=esi_item_id,
                    parent_esi_item_id=parent_esi_item_id,
                    is_blueprint_copy=is_blueprint_copy,
                    quantity=qty, universe_station_id=station_id,
                    universe_structure_id=structure_id,
                    location_flag=location_flag, location_type=location_type,
                    touched=True,
                )
                db.session.add(bpc)

        UserAsset.query.filter_by(user_id=user.id, touched=False).delete()

        # Sync owned blueprints and compute invention potentials from the same ESI page data.
        from evebs.models import Blueprint
        from evebs.models.tables.associations import user_blueprints
        known = {bp.id for bp in Blueprint.query.all()}
        bp_ids = list({a['type_id'] for a in pages if a.get('type_id') in known})

        db.session.execute(
            user_blueprints.delete().where(user_blueprints.c.user_id == user.id)
        )
        for bp_id in bp_ids:
            db.session.execute(
                user_blueprints.insert().values(user_id=user.id, blueprint_id=bp_id)
            )

        activities, bp_to_produced = _load_blueprint_activities()
        _generate_potential_assets(user, activities, bp_to_produced)
        user.last_blueprints_download = datetime.utcnow()

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
