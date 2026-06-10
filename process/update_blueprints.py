#!/usr/bin/env python3
"""Upsert Blueprint rows from data/manufacturing_tree.json, compute manufacturing_cost,
and populate is_invented_by from data/eve_static_data/blueprints.jsonl.

manufacturing_cost = SUM(material_quantity × jita_prices.min_sell_price) for each
blueprint's direct materials.  NULL when any material has no Jita price.
"""
import argparse
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

MANUFACTURING_TREE = os.path.join(os.path.dirname(__file__), '..', 'data', 'manufacturing_tree.json')
BLUEPRINTS_JSONL   = os.path.join(os.path.dirname(__file__), '..', 'data', 'eve_static_data', 'blueprints.jsonl')


def load_manufacturing_tree(path: str) -> dict:
    """Load the manufacturing/reaction BOM tree from JSON.

    Args:
        path: Absolute path to manufacturing_tree.json.

    Returns:
        Dict mapping str(produced_type_id) → entry dict with keys
        name, activity_type, manufacturing_level, prod_qty, chain.
    """
    with open(path) as f:
        return json.load(f)


def build_item_map() -> dict:
    """Query all EveItem rows and index them by id.

    Returns:
        Dict mapping int type_id → EveItem instance.
    """
    from evebs.models import EveItem
    item_map = {ei.id: ei for ei in EveItem.query.all()}
    logger.debug('Item map: %d items loaded.', len(item_map))
    return item_map


def build_price_map() -> dict:
    """Query all JitaMarketAnalytics rows and index min_sell_price by type_id.

    Returns:
        Dict mapping int type_id → float min_sell_price.
    """
    from evebs.models import JitaMarketAnalytics
    price_map = {jma.id: jma.min_sell_price for jma in JitaMarketAnalytics.query.all()}
    logger.debug('Jita price map: %d prices loaded.', len(price_map))
    return price_map


def build_blueprint_map() -> dict:
    """Query all Blueprint rows and index them by produced_type_id.

    Returns:
        Dict mapping int produced_type_id → Blueprint instance.
    """
    from evebs.models import Blueprint
    bp_map = {bp.produced_type_id: bp for bp in Blueprint.query.all()}
    logger.debug('Blueprint map: %d blueprints loaded.', len(bp_map))
    return bp_map


def compute_cost(chain: dict, price_map: dict) -> float | None:
    """Compute total manufacturing cost from direct materials and Jita prices.

    Args:
        chain:     Top-level BOM dict — str(mat_type_id) → {quantity, chain, ...}.
        price_map: Dict mapping int type_id → float Jita min_sell_price.

    Returns:
        Total ISK cost for one production batch, or None if any material has no price.
    """
    cost = 0.0
    for mat_id_str, mat_entry in chain.items():
        price = price_map.get(int(mat_id_str))
        if price is None:
            return None
        cost += mat_entry['quantity'] * price
    return cost


def upsert_blueprints(
    tree: dict,
    item_map: dict,
    price_map: dict,
    bp_map: dict,
    *,
    dry_run: bool = False,
) -> tuple[int, int, int]:
    """Upsert Blueprint rows from the manufacturing tree.

    Creates new Blueprint rows for entries absent from the DB and updates
    existing ones.  Also sets production_level and blueprint_id on EveItem.

    Args:
        tree:      manufacturing_tree.json content (str type_id → entry).
        item_map:  int type_id → EveItem.
        price_map: int type_id → float Jita price.
        bp_map:    int produced_type_id → Blueprint (mutated in-place).
        dry_run:   When True, compute counts but do not add/flush anything.

    Returns:
        (new_count, updated_count, no_price_count)
    """
    from evebs.extensions import db
    from evebs.models import Blueprint

    new_count = updated_count = no_price_count = 0

    for type_id_str, entry in tree.items():
        produced_type_id    = int(type_id_str)
        prod_qty            = entry['prod_qty']
        manufacturing_level = entry['manufacturing_level']
        activity_type       = entry.get('activity_type', 'manufacturing')
        chain               = entry['chain']
        manufacturing_cost  = compute_cost(chain, price_map)

        if manufacturing_cost is None:
            no_price_count += 1

        produced_item = item_map.get(produced_type_id)

        bp = bp_map.get(produced_type_id)
        if bp:
            if not dry_run:
                bp.prod_qtt           = prod_qty
                bp.activity_type      = activity_type
                bp.manufacturing_cost = manufacturing_cost
                bp.manufacturing_tree = chain
            logger.debug(
                'Updated blueprint %d (%s): prod_qtt=%d, cost=%s.',
                produced_type_id, bp.name, prod_qty, manufacturing_cost,
            )
            updated_count += 1
        else:
            bp_name = produced_item.name if produced_item else f'Unknown ({produced_type_id})'
            if not dry_run:
                bp = Blueprint(
                    id                 = produced_type_id,
                    produced_type_id   = produced_type_id,
                    nb_runs            = 1,
                    prod_qtt           = prod_qty,
                    name               = bp_name,
                    activity_type      = activity_type,
                    manufacturing_cost = manufacturing_cost,
                    manufacturing_tree = chain,
                )
                db.session.add(bp)
                db.session.flush()
                bp_map[produced_type_id] = bp
            logger.debug(
                'Created blueprint %d (%s): prod_qtt=%d, cost=%s.',
                produced_type_id, bp_name, prod_qty, manufacturing_cost,
            )
            new_count += 1

        if not dry_run and produced_item:
            produced_item.production_level = manufacturing_level
            produced_item.blueprint_id     = bp.id

    return new_count, updated_count, no_price_count


def update_invented_by(bp_map: dict, *, dry_run: bool = False) -> int:
    """Populate is_invented_by on T2 Blueprint rows from blueprints.jsonl.

    For each SDE blueprint entry that has both a manufacturing and an invention
    activity, the T1 blueprint's produced_type_id is written as is_invented_by
    on every T2 blueprint it can invent.

    Only updates blueprints that already exist in bp_map (i.e. in the DB).
    Entries with no manufacturing activity (rare edge cases) are skipped.

    Args:
        bp_map:  int produced_type_id → Blueprint (mutated in-place).
        dry_run: When True, count but do not mutate blueprints.

    Returns:
        Number of Blueprint rows updated.
    """
    updated = 0
    with open(BLUEPRINTS_JSONL) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry      = json.loads(line)
            activities = entry.get('activities', {})
            mfg        = activities.get('manufacturing')
            inv        = activities.get('invention')
            if not mfg or not inv:
                continue

            mfg_products = mfg.get('products', [])
            inv_products = inv.get('products', [])
            if not mfg_products or not inv_products:
                continue

            t1_id = mfg_products[0]['typeID']

            for product in inv_products:
                t2_id = product['typeID']
                bp = bp_map.get(t2_id)
                if bp is None:
                    continue
                if not dry_run:
                    bp.is_invented_by = t1_id
                updated += 1
                logger.debug(
                    'Blueprint %d (%s) is_invented_by → %d.',
                    t2_id, bp.name, t1_id,
                )

    return updated


def main() -> None:
    """Parse args, open app context, and run upsert + invention-link passes."""
    parser = argparse.ArgumentParser(description='Upsert blueprints from manufacturing_tree.json.')
    parser.add_argument('-n', '--no-op', action='store_true',
                        help='Dry-run: print counts without writing.')
    args = parser.parse_args()

    from app import app

    with app.app_context():
        from evebs.extensions import db

        tree = load_manufacturing_tree(MANUFACTURING_TREE)

        if args.no_op:
            logger.info('Dry-run — manufacturing_tree.json has %d entries.', len(tree))
            from evebs.models import Blueprint
            logger.info('Blueprints in DB: %d', Blueprint.query.count())
            bp_map = build_blueprint_map()
            invented = update_invented_by(bp_map, dry_run=True)
            logger.info('Would update is_invented_by on %d blueprints.', invented)
            sys.exit(0)

        item_map  = build_item_map()
        price_map = build_price_map()
        bp_map    = build_blueprint_map()

        new_count, updated_count, no_price_count = upsert_blueprints(
            tree, item_map, price_map, bp_map,
        )
        invented_count = update_invented_by(bp_map)

        db.session.commit()
        logger.info(
            'Done — Blueprint: %d new, %d updated | %d had no Jita price (manufacturing_cost=NULL) | '
            '%d is_invented_by links set.',
            new_count, updated_count, no_price_count, invented_count,
        )


if __name__ == '__main__':
    main()
