#!/usr/bin/env python3
"""Build a manufacturing tree from eve_static_data/blueprints.jsonl and save as JSON."""
import json
import os

BLUEPRINTS_FILE = os.path.join(os.path.dirname(__file__), 'eve_static_data', 'blueprints.jsonl')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'manufacturing_tree.json')


def _load_bp_index(path):
    bp_index = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            bp = json.loads(line)
            mfg = bp.get('activities', {}).get('manufacturing')
            if not mfg:
                continue
            products = mfg.get('products', [])
            if not products:
                continue
            produced_id = products[0]['typeID']
            prod_qty = products[0].get('quantity', 1)
            bp_index[produced_id] = {
                'materials': mfg.get('materials', []),
                'prod_qty': prod_qty,
            }
    return bp_index


def _compute_level_and_chain(type_id, bp_index, visited=None):
    if visited is None:
        visited = set()

    if type_id in visited or type_id not in bp_index:
        return 0, {}

    visited = visited | {type_id}
    chain = {}
    max_sub_level = 0

    for mat in bp_index[type_id]['materials']:
        mat_id = mat['typeID']
        sub_level, sub_chain = _compute_level_and_chain(mat_id, bp_index, visited)
        if sub_level > max_sub_level:
            max_sub_level = sub_level
        chain[mat_id] = {'quantity': mat['quantity'], 'chain': sub_chain}

    return max_sub_level + 1, chain


def build_manufacturing_tree():
    print(f'Reading {BLUEPRINTS_FILE}...')
    bp_index = _load_bp_index(BLUEPRINTS_FILE)
    print(f'Loaded {len(bp_index)} manufacturing blueprints.')

    tree = {}
    for type_id, bp in bp_index.items():
        level, chain = _compute_level_and_chain(type_id, bp_index)
        tree[type_id] = {
            'manufacturing_level': level,
            'prod_qty': bp['prod_qty'],
            'chain': chain,
        }

    print(f'Writing {OUTPUT_FILE}...')
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(tree, f, indent=2)
    print(f'Done. {len(tree)} items written.')


if __name__ == '__main__':
    build_manufacturing_tree()
