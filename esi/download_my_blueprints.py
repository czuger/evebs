import json
import logging
import os
from datetime import datetime

from evebs.extensions import db
from esi.client import EsiClient

logger = logging.getLogger(__name__)

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

        # Source counts as a BPC if it's a real BPC OR a potential that was itself invented
        # (an invented T2 BPC can be used for further invention without any copy step)
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
    from evebs.models.tables.bpc_asset import BpcAsset

    db.session.query(BpcAsset).filter_by(user_id=user.id, is_potential=True).delete()

    real = db.session.query(BpcAsset).filter_by(user_id=user.id, is_potential=False).all()
    real_bpo_ids = {a.eve_item_id for a in real if not a.is_blueprint_copy}
    real_bpc_ids = {a.eve_item_id for a in real if a.is_blueprint_copy}

    potentials = _compute_potentials(real_bpo_ids, real_bpc_ids, activities)

    inserted = 0
    for blueprint_type_id, potential_type in potentials.items():
        produced_type_id = bp_to_produced.get(blueprint_type_id)
        if produced_type_id is None:
            continue
        db.session.add(BpcAsset(
            user_id=user.id,
            eve_item_id=produced_type_id,
            is_blueprint_copy=True,
            is_potential=True,
            potential_type=potential_type,
            quantity=0,
        ))
        inserted += 1

    logger.info('Generated %d potential blueprint entries for user %s', inserted, user.id)


def download_my_blueprints(user):
    from evebs.models import Blueprint
    from evebs.models.tables.associations import user_blueprints

    client = EsiClient(f'characters/{user.uid}/assets/')
    if not client.set_auth_token(user):
        logger.warning('Could not set auth token for user %s', user.id)
        return False

    pages = client.get_all_pages()
    if pages is None:
        logger.warning('No data returned from ESI for user %s', user.id)
        return False

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
    db.session.commit()
    logger.info('Blueprints refreshed for user %s: %d found', user.id, len(bp_ids))
    return True
