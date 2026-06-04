#!/usr/bin/env python3
"""Build a combined manufacturing + reaction tree from eve_static_data/ and save as JSON.

Output file:
    manufacturing_tree.json  — all manufacturing and reaction blueprints in one file

Output structure:
    {
        "<typeID>": {
            "name": "<produced item name>",
            "activity_type": "manufacturing" | "reaction",
            "manufacturing_level": <int>,   # 0 = raw, n = deepest component is at n-1
            "prod_qty": <int>,              # units produced per blueprint run
            "chain": {
                "<mat_typeID>": {
                    "name": "<material name>",
                    "quantity": <int>,      # units of this material required
                    "chain": { ... }        # recursive sub-tree (empty for raw materials)
                },
                ...
            }
        },
        ...
    }
"""
import json
import os

DATA_DIR        = os.path.dirname(__file__)
BLUEPRINTS_FILE = os.path.join(DATA_DIR, 'eve_static_data', 'blueprints.jsonl')
TYPES_FILE      = os.path.join(DATA_DIR, 'eve_static_data', 'types.jsonl')
OUTPUT_FILE     = os.path.join(DATA_DIR, 'manufacturing_tree.json')

# Type aliases for readability
NameIndex = dict[int, str]            # type_id → english name
BpIndex   = dict[int, dict]           # produced_type_id → {materials, prod_qty}
Chain     = dict[str, dict]           # str(mat_type_id) → {name, quantity, chain}


def _load_name_index(path: str) -> NameIndex:
    """Load English item names from types.jsonl.

    Args:
        path: Absolute path to types.jsonl.

    Returns:
        Dict mapping typeID → English name string.
    """
    index: NameIndex = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            type_id = obj.get('_key')
            name = obj.get('name', {})
            en_name = name.get('en') if isinstance(name, dict) else name
            if type_id is not None and en_name:
                index[type_id] = en_name
    return index


def _load_bp_index(path: str) -> tuple[BpIndex, dict[int, str]]:
    """Parse blueprints.jsonl and index all manufacturing and reaction blueprints.

    Manufacturing takes precedence when a blueprint has both activities.
    Invention, copying, and research activities are always ignored.

    Args:
        path: Absolute path to blueprints.jsonl.

    Returns:
        (bp_index, activity_map) where:
          bp_index      maps produced_type_id → {'materials': [...], 'prod_qty': int}
          activity_map  maps produced_type_id → 'manufacturing' | 'reaction'
    """
    bp_index: BpIndex = {}
    activity_map: dict[int, str] = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            bp = json.loads(line)
            activities = bp.get('activities', {})
            mfg = activities.get('manufacturing')
            rxn = activities.get('reaction')
            act = mfg or rxn
            if not act:
                continue
            activity_type = 'manufacturing' if mfg else 'reaction'

            products = act.get('products', [])
            if not products:
                continue

            produced_id: int = products[0]['typeID']
            prod_qty: int = products[0].get('quantity', 1)

            bp_index[produced_id] = {
                'materials': act.get('materials', []),
                'prod_qty': prod_qty,
            }
            activity_map[produced_id] = activity_type

    return bp_index, activity_map


def _compute_level_and_chain(
    type_id: int,
    bp_index: BpIndex,
    name_index: NameIndex,
    visited: set[int] | None = None,
) -> tuple[int, Chain]:
    """Recursively compute the manufacturing level and component chain for one item.

    Manufacturing level:
        0  — raw material (no blueprint, or cycle detected)
        n  — the deepest direct or indirect component sits at level n-1

    Cycle guard: the visited set tracks ancestors on the current recursion path
    to prevent infinite loops from circular blueprint references in the data.

    Args:
        type_id:    EVE typeID of the item to evaluate.
        bp_index:   Full blueprint index built by _load_bp_index.
        name_index: Type name lookup built by _load_name_index.
        visited:    Set of typeIDs already on the current recursion stack.

    Returns:
        (level, chain) where chain maps str(mat_type_id) →
        {'name': str, 'quantity': int, 'chain': Chain}.
    """
    if visited is None:
        visited = set()

    # Base case: raw material or cycle — no further decomposition
    if type_id in visited or type_id not in bp_index:
        return 0, {}

    visited = visited | {type_id}
    chain: Chain = {}
    max_sub_level = 0

    for mat in bp_index[type_id]['materials']:
        mat_id: int = mat['typeID']
        sub_level, sub_chain = _compute_level_and_chain(mat_id, bp_index, name_index, visited)

        if sub_level > max_sub_level:
            max_sub_level = sub_level

        chain[str(mat_id)] = {
            'name': name_index.get(mat_id, str(mat_id)),
            'quantity': mat['quantity'],
            'chain': sub_chain,
        }

    return max_sub_level + 1, chain


def build_manufacturing_tree() -> None:
    """Build the combined manufacturing + reaction tree and write to OUTPUT_FILE.

    Output is consumed by process/update_eve_item_costs.py (manufacturing entries)
    and serves as reference data for reaction cost analysis (reaction entries).
    """
    print(f'Reading type names from {TYPES_FILE}...')
    name_index = _load_name_index(TYPES_FILE)
    print(f'Loaded {len(name_index)} type names.')

    print(f'Reading blueprints from {BLUEPRINTS_FILE}...')
    bp_index, activity_map = _load_bp_index(BLUEPRINTS_FILE)
    n_mfg = sum(1 for v in activity_map.values() if v == 'manufacturing')
    n_rxn = sum(1 for v in activity_map.values() if v == 'reaction')
    print(f'Loaded {n_mfg} manufacturing + {n_rxn} reaction blueprints.')

    print('Building tree...')
    tree: dict = {}
    for type_id, bp in bp_index.items():
        level, chain = _compute_level_and_chain(type_id, bp_index, name_index)
        tree[str(type_id)] = {
            'name': name_index.get(type_id, str(type_id)),
            'activity_type': activity_map[type_id],
            'manufacturing_level': level,
            'prod_qty': bp['prod_qty'],
            'chain': chain,
        }

    print(f'Writing {OUTPUT_FILE}...')
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(tree, f, indent=2)
    print(f'Done. {len(tree)} items written ({n_mfg} manufacturing, {n_rxn} reaction).')


if __name__ == '__main__':
    build_manufacturing_tree()
