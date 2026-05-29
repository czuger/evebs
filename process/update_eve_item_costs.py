#!/usr/bin/env python3
"""Update EveItem.cost from Jita sell orders, processing manufacturing levels bottom-up."""
import json
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import setup_logging
import logging
setup_logging()
logger = logging.getLogger(__name__)

from sqlalchemy import text
from evebs.extensions import db
from evebs.models import EveItem, TradeHub, Constant

MANUFACTURING_TREE = os.path.join(os.path.dirname(__file__), '..', 'data', 'manufacturing_tree.json')
JITA_SYSTEM_ID = 30000142
TARGET_QTY = 1000


def _load_jita_prices(jita_hub_id):
    """Return {eve_item_id: [(price, volume_remain), ...]} with the 10 cheapest sell orders per item."""
    rows = db.session.execute(text("""
        SELECT eve_item_id, price, volume_remain
        FROM (
            SELECT eve_item_id, price, volume_remain,
                   ROW_NUMBER() OVER (PARTITION BY eve_item_id ORDER BY price) AS rn
            FROM public_trade_orders
            WHERE trade_hub_id = :hub_id AND is_buy_order = FALSE
        ) sub
        WHERE rn <= 10
    """), {'hub_id': jita_hub_id}).fetchall()

    prices = {}
    for eve_item_id, price, volume in rows:
        prices.setdefault(eve_item_id, []).append((price, volume))
    return prices


def _compute_vwap(orders):
    """VWAP to fill up to TARGET_QTY units from [(price, volume), ...] sorted by price asc."""
    if not orders:
        return None
    total_volume = sum(v for _, v in orders)
    fill = min(TARGET_QTY, total_volume)
    remaining = fill
    total_cost = 0.0
    for price, volume in orders:
        take = min(volume, remaining)
        total_cost += take * price
        remaining -= take
        if remaining <= 0:
            break
    return total_cost / fill


def update_eve_item_cost():
    t_start = time.time()
    logger.info('=== update_eve_item_cost started ===')

    jita = TradeHub.query.filter_by(eve_system_id=JITA_SYSTEM_ID).first()
    if not jita:
        logger.error('Jita trade hub not found (eve_system_id=%d).', JITA_SYSTEM_ID)
        return
    jita_hub_id = jita.id

    t = time.time()
    with open(MANUFACTURING_TREE) as f:
        tree = json.load(f)
    logger.debug('Manufacturing tree loaded: %d entries in %.2fs.', len(tree), time.time() - t)

    taxes_const = Constant.query.filter_by(libe='taxes').first()
    taxes = taxes_const.f_value if taxes_const else 1.0

    t = time.time()
    item_map = {item.cpp_eve_item_id: item for item in EveItem.query.all()}
    logger.debug('Item map built: %d items in %.2fs.', len(item_map), time.time() - t)

    t = time.time()
    jita_prices = _load_jita_prices(jita_hub_id)
    logger.info('Jita prices loaded: %d items in %.2fs.', len(jita_prices), time.time() - t)

    LOG_EVERY = 1000

    # Level 0: base items not in the manufacturing tree
    t = time.time()
    t_checkpoint = time.time()
    tree_ids = {int(k) for k in tree}
    base_items = [item for item in item_map.values() if item.cpp_eve_item_id not in tree_ids]
    for i, item in enumerate(base_items, 1):
        item.cost = _compute_vwap(jita_prices.get(item.id, []))
        if i % LOG_EVERY == 0:
            logger.info('Level 0: %d items updated in %.2fs.', i, time.time() - t_checkpoint)
            t_checkpoint = time.time()
    db.session.commit()
    logger.info('Level 0 done: %d base items updated in %.2fs.', len(base_items), time.time() - t)

    # Levels 1…n: manufactured items, ascending
    by_level = {}
    for type_id_str, entry in tree.items():
        lvl = entry['manufacturing_level']
        by_level.setdefault(lvl, []).append((int(type_id_str), entry))

    for level in sorted(by_level):
        t = time.time()
        t_checkpoint = time.time()
        batch = by_level[level]
        processed = 0
        for type_id, entry in batch:
            item = item_map.get(type_id)
            if not item:
                continue
            chain = entry['chain']
            prod_qty = entry['prod_qty']
            total = 0.0
            unknown = False
            for mat_id_str, mat in chain.items():
                comp = item_map.get(int(mat_id_str))
                if comp is None or comp.cost is None:
                    unknown = True
                    break
                total += comp.cost * mat['quantity']
            item.cost = None if unknown else (total * taxes / prod_qty)
            processed += 1
            if processed % LOG_EVERY == 0:
                logger.info('Level %d: %d items updated in %.2fs.', level, processed, time.time() - t_checkpoint)
                t_checkpoint = time.time()
        db.session.commit()
        logger.info('Level %d done: %d items updated in %.2fs.', level, processed, time.time() - t)

    logger.info('=== update_eve_item_cost finished in %.2fs ===', time.time() - t_start)


if __name__ == '__main__':
    from app import app
    with app.app_context():
        update_eve_item_cost()
