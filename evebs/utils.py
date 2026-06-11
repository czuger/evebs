import json
import os
from functools import lru_cache

_BLUEPRINTS_FILE = os.path.join(
    os.path.dirname(__file__), '..', 'data', 'eve_static_data', 'blueprints.jsonl'
)


@lru_cache(maxsize=1)
def blueprint_type_to_produced():
    """Map each manufacturing blueprintTypeID → produced item type_id (from the EVE SDE).

    Used to resolve copying/invention industry jobs (keyed by blueprint type id) back
    to the manufactured item shown in the buy/sell order tables.
    """
    mapping = {}
    with open(_BLUEPRINTS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            bp = json.loads(line)
            bp_id = bp.get('_key')
            products = bp.get('activities', {}).get('manufacturing', {}).get('products', [])
            if bp_id is not None and products:
                mapping[bp_id] = products[0]['typeID']
    return mapping


_COPYING_ACTIVITY = 5
_INVENTION_ACTIVITY = 8


def active_job_item_sets(jobs):
    """Split active industry jobs into produced-item id sets per activity.

    `jobs` is an iterable of rows with `activity_id`, `product_type_id` and
    `blueprint_type_id`. Returns (manufacturing_item_ids, copying_item_ids,
    inventing_item_ids), each a set of produced item type ids — copying and
    invention jobs are resolved back to the manufactured item via the SDE map.
    """
    bp_to_produced = blueprint_type_to_produced()
    manufacturing_item_ids, copying_item_ids, inventing_item_ids = set(), set(), set()
    for job in jobs:
        if job.activity_id == _COPYING_ACTIVITY:
            produced = bp_to_produced.get(job.blueprint_type_id)
            if produced is not None:
                copying_item_ids.add(produced)
        elif job.activity_id == _INVENTION_ACTIVITY:
            produced = bp_to_produced.get(job.product_type_id)
            if produced is not None:
                inventing_item_ids.add(produced)
        elif job.product_type_id is not None:
            manufacturing_item_ids.add(job.product_type_id)
    return manufacturing_item_ids, copying_item_ids, inventing_item_ids


class SimplePagination:
    """Pagination helper compatible with shared/pagination.html."""

    def __init__(self, page: int, per_page: int, total: int):
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = max(1, (total + per_page - 1) // per_page)
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_num = page - 1
        self.next_num = page + 1

    def iter_pages(self, left_edge=2, right_edge=2, left_current=2, right_current=3):
        last = 0
        for num in range(1, self.pages + 1):
            if (num <= left_edge
                    or self.page - left_current - 1 < num < self.page + right_current
                    or num > self.pages - right_edge):
                if last + 1 != num:
                    yield None
                yield num
                last = num
