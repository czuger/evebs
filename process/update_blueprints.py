#!/usr/bin/env python3
"""Upsert Blueprint and BlueprintMaterial from data/manufacturing_tree.json."""
import argparse
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
from config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

MANUFACTURING_TREE = os.path.join(os.path.dirname(__file__), '..', 'data', 'manufacturing_tree.json')

parser = argparse.ArgumentParser(description='Upsert blueprints from manufacturing_tree.json.')
parser.add_argument('-n', '--no-op', action='store_true',
                    help='Dry-run: print counts without writing.')
args = parser.parse_args()

from app import app

with app.app_context():
    from evebs.extensions import db
    from evebs.models import EveItem, Blueprint, BlueprintMaterial

    with open(MANUFACTURING_TREE) as f:
        tree = json.load(f)

    if args.no_op:
        logger.info('Dry-run — manufacturing_tree.json has %d entries.', len(tree))
        logger.info('Blueprints in DB: %d', Blueprint.query.count())
        logger.info('BlueprintMaterials in DB: %d', BlueprintMaterial.query.count())
        sys.exit(0)

    logger.debug('Loading item map...')
    item_map = {ei.id: ei for ei in EveItem.query.all()}
    logger.debug('Item map: %d items loaded.', len(item_map))

    logger.debug('Loading blueprint map...')
    bp_map = {bp.produced_type_id: bp for bp in Blueprint.query.all()}
    logger.debug('Blueprint map: %d blueprints loaded.', len(bp_map))

    logger.debug('Processing %d tree entries...', len(tree))
    new_count = updated_count = mat_count = skipped_count = 0

    for type_id_str, entry in tree.items():
        produced_cpp_id     = int(type_id_str)
        prod_qty            = entry['prod_qty']
        manufacturing_level = entry['manufacturing_level']
        chain               = entry['chain']

        produced_item = item_map.get(produced_cpp_id)

        bp = bp_map.get(produced_cpp_id)
        if bp:
            bp.prod_qtt = prod_qty
            BlueprintMaterial.query.filter_by(blueprint_id=bp.id).delete()
            logger.debug('Updated blueprint %d (%s): prod_qtt=%d, %d materials cleared.',
                         produced_cpp_id, bp.name, prod_qty,
                         len(chain))
            updated_count += 1
        else:
            bp_name = produced_item.name if produced_item else f'Unknown ({produced_cpp_id})'
            bp = Blueprint(
                id               = produced_cpp_id,
                produced_type_id = produced_cpp_id,
                nb_runs          = 1,
                prod_qtt         = prod_qty,
                name             = bp_name,
            )
            db.session.add(bp)
            db.session.flush()
            bp_map[produced_cpp_id] = bp
            logger.debug('Created blueprint %d (%s): prod_qtt=%d.', produced_cpp_id, bp_name, prod_qty)
            new_count += 1

        if produced_item:
            produced_item.production_level = manufacturing_level
            produced_item.blueprint_id     = bp.id

        entry_mat_count = 0
        for mat_id_str, mat_entry in chain.items():
            mat_item = item_map.get(int(mat_id_str))
            if not mat_item:
                logger.debug('Skipped unknown material cpp_id=%s for blueprint %d.', mat_id_str, produced_cpp_id)
                skipped_count += 1
                continue
            db.session.add(BlueprintMaterial(
                blueprint_id = bp.id,
                required_qtt = mat_entry['quantity'],
                eve_item_id  = mat_item.id,
            ))
            mat_count += 1
            entry_mat_count += 1

        logger.debug('Blueprint %d: %d materials written.', produced_cpp_id, entry_mat_count)

    logger.debug('Committing...')
    db.session.commit()
    logger.info(
        'Done — Blueprint: %d new, %d updated | BlueprintMaterial: %d written | %d materials skipped (unknown item)',
        new_count, updated_count, mat_count, skipped_count,
    )
