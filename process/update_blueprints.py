#!/usr/bin/env python3
"""Upsert Blueprint rows from data/manufacturing_tree.json and compute manufacturing_cost.

manufacturing_cost = SUM(material_quantity × jita_prices.min_sell_price) for each
blueprint's direct materials.  NULL when any material has no Jita price.
"""
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
    from evebs.models import EveItem, Blueprint, JitaPrices

    with open(MANUFACTURING_TREE) as f:
        tree = json.load(f)

    if args.no_op:
        logger.info('Dry-run — manufacturing_tree.json has %d entries.', len(tree))
        logger.info('Blueprints in DB: %d', Blueprint.query.count())
        sys.exit(0)

    logger.debug('Loading item map...')
    item_map = {ei.id: ei for ei in EveItem.query.all()}
    logger.debug('Item map: %d items loaded.', len(item_map))

    logger.debug('Loading Jita prices...')
    price_map = {jp.id: jp.min_sell_price for jp in JitaPrices.query.all()}
    logger.debug('Jita price map: %d prices loaded.', len(price_map))

    logger.debug('Loading blueprint map...')
    bp_map = {bp.produced_type_id: bp for bp in Blueprint.query.all()}
    logger.debug('Blueprint map: %d blueprints loaded.', len(bp_map))

    logger.debug('Processing %d tree entries...', len(tree))
    new_count = updated_count = skipped_count = no_price_count = 0

    for type_id_str, entry in tree.items():
        produced_cpp_id     = int(type_id_str)
        prod_qty            = entry['prod_qty']
        manufacturing_level = entry['manufacturing_level']
        activity_type       = entry.get('activity_type', 'manufacturing')
        chain               = entry['chain']

        produced_item = item_map.get(produced_cpp_id)

        # Compute manufacturing_cost from direct chain × Jita prices
        cost = 0.0
        missing_price = False
        for mat_id_str, mat_entry in chain.items():
            price = price_map.get(int(mat_id_str))
            if price is None:
                missing_price = True
                break
            cost += mat_entry['quantity'] * price
        manufacturing_cost = None if missing_price else cost

        if missing_price:
            no_price_count += 1

        bp = bp_map.get(produced_cpp_id)
        if bp:
            bp.prod_qtt            = prod_qty
            bp.activity_type       = activity_type
            bp.manufacturing_cost  = manufacturing_cost
            bp.manufacturing_tree  = chain
            logger.debug('Updated blueprint %d (%s): prod_qtt=%d, cost=%s.',
                         produced_cpp_id, bp.name, prod_qty, manufacturing_cost)
            updated_count += 1
        else:
            bp_name = produced_item.name if produced_item else f'Unknown ({produced_cpp_id})'
            bp = Blueprint(
                id                 = produced_cpp_id,
                produced_type_id   = produced_cpp_id,
                nb_runs            = 1,
                prod_qtt           = prod_qty,
                name               = bp_name,
                activity_type      = activity_type,
                manufacturing_cost = manufacturing_cost,
                manufacturing_tree = chain,
            )
            db.session.add(bp)
            db.session.flush()
            bp_map[produced_cpp_id] = bp
            logger.debug('Created blueprint %d (%s): prod_qtt=%d, cost=%s.',
                         produced_cpp_id, bp_name, prod_qty, manufacturing_cost)
            new_count += 1

        if produced_item:
            produced_item.production_level = manufacturing_level
            produced_item.blueprint_id     = bp.id

    db.session.commit()
    logger.info(
        'Done — Blueprint: %d new, %d updated | %d had no Jita price (manufacturing_cost=NULL)',
        new_count, updated_count, no_price_count,
    )
