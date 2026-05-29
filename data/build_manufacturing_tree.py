#!/usr/bin/env python3
"""Build a manufacturing tree from eve_static_data/blueprints.jsonl and save as JSON.

Output structure (manufacturing_tree.json):
    {
        "<typeID>": {
            "manufacturing_level": <int>,   # 0 = raw, n = deepest component is at n-1
            "prod_qty": <int>,              # units produced per blueprint run
            "chain": {
                "<mat_typeID>": {
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

# Input: EVE static data dump, one blueprint JSON object per line
BLUEPRINTS_FILE = os.path.join(os.path.dirname(__file__), 'eve_static_data', 'blueprints.jsonl')
# Output: pre-computed manufacturing tree consumed by process/update_eve_item_costs.py
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'manufacturing_tree.json')

# Type aliases for readability
BpIndex = dict[int, dict]          # produced_type_id → {materials, prod_qty}
Chain   = dict[int, dict]          # mat_type_id → {quantity, chain}


def _load_bp_index(path: str) -> BpIndex:
    """Parse blueprints.jsonl and index blueprints by the typeID they produce.

    Both manufacturing and reaction activities are included. Invention, copying,
    and research activities are ignored. When a blueprint has both activities,
    manufacturing takes precedence.

    Args:
        path: Absolute path to blueprints.jsonl.

    Returns:
        Dict mapping produced_type_id → {'materials': [...], 'prod_qty': int}.
        Each material entry is {'typeID': int, 'quantity': int}.
    """
    bp_index: BpIndex = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            bp = json.loads(line)
            activities = bp.get('activities', {})
            # Prefer manufacturing; fall back to reaction
            activity = activities.get('manufacturing') or activities.get('reaction')
            if not activity:
                continue

            products = activity.get('products', [])
            if not products:
                continue

            produced_id: int = products[0]['typeID']
            prod_qty: int = products[0].get('quantity', 1)

            bp_index[produced_id] = {
                'materials': activity.get('materials', []),
                'prod_qty': prod_qty,
            }

    return bp_index


def _compute_level_and_chain(
    type_id: int,
    bp_index: BpIndex,
    visited: set[int] | None = None,
) -> tuple[int, Chain]:
    """Recursively compute the manufacturing level and component chain for one item.

    Manufacturing level:
        0  — raw material (no blueprint, or cycle detected)
        n  — the deepest direct or indirect component sits at level n-1

    Cycle guard: the visited set tracks ancestors on the current recursion path
    to prevent infinite loops from circular blueprint references in the data.

    Args:
        type_id:  EVE typeID of the item to evaluate.
        bp_index: Full blueprint index built by _load_bp_index.
        visited:  Set of typeIDs already on the current recursion stack.

    Returns:
        (level, chain) where chain maps mat_type_id → {'quantity': int, 'chain': Chain}.
    """
    if visited is None:
        visited = set()

    # Base case: raw material or cycle — no further decomposition
    if type_id in visited or type_id not in bp_index:
        return 0, {}

    # Add current item to the path before recursing into its components
    visited = visited | {type_id}
    chain: Chain = {}
    max_sub_level = 0

    for mat in bp_index[type_id]['materials']:
        mat_id: int = mat['typeID']
        sub_level, sub_chain = _compute_level_and_chain(mat_id, bp_index, visited)

        # Track the deepest sub-level to determine this item's own level
        if sub_level > max_sub_level:
            max_sub_level = sub_level

        chain[mat_id] = {'quantity': mat['quantity'], 'chain': sub_chain}

    # This item sits one level above its deepest component
    return max_sub_level + 1, chain


def build_manufacturing_tree() -> None:
    """Build the full manufacturing tree and write it to OUTPUT_FILE as pretty JSON.

    Reads all blueprints, computes the manufacturing level and recursive component
    chain for every manufactured item, then serialises the result.  The output is
    consumed at runtime by process/update_eve_item_costs.py to propagate item costs
    from raw materials up through manufactured goods layer by layer.
    """
    print(f'Reading {BLUEPRINTS_FILE}...')
    bp_index = _load_bp_index(BLUEPRINTS_FILE)
    print(f'Loaded {len(bp_index)} manufacturing/reaction blueprints.')

    tree: dict[int, dict] = {}
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
