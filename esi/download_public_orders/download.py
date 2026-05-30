import logging
import time
from datetime import datetime

from evebs.extensions import db
from evebs.models import PublicTradeOrder

from esi.download_public_orders.reference_data import load_reference_data
from esi.download_public_orders.fetch import (
    fetch_region_types, fetch_type_orders, fetch_region_all_orders,
)
from esi.download_public_orders.upsert import (
    load_snapshot_for, classify_orders, apply_batch, record_sold_out_orders,
)

logger = logging.getLogger(__name__)


def download(
    essentials:  bool = False,
    forge_only:  bool = False,
    all_at_once: bool = False,
) -> None:
    t0 = time.perf_counter()

    hub_map, item_map, regions = load_reference_data(essentials, forge_only)
    logger.debug('Reference data loaded: %d hubs | %d items', len(hub_map), len(item_map))

    PublicTradeOrder.query.update({'touched': False})
    db.session.flush()

    item_map_keys  = set(item_map.keys())
    created = updated = touched = 0
    skipped_no_hub = skipped_zero = 0
    sales_created  = 0

    for region in regions:
        if all_at_once:
            raw_orders = fetch_region_all_orders(region)
        else:
            region_type_ids = fetch_region_types(region)
            relevant_types  = region_type_ids & item_map_keys
            logger.debug('%s: %d/%d types tracked',
                         region.name, len(relevant_types), len(region_type_ids))
            raw_orders = []
            for type_id in relevant_types:
                raw_orders.extend(fetch_type_orders(region, type_id))

        pending = []
        for od in raw_orders:
            item_id = item_map.get(od.get('type_id'))
            if item_id is None:
                continue
            hub_id = hub_map.get(od.get('system_id'))
            if not hub_id:
                skipped_no_hub += 1
                continue
            if od.get('volume_remain', 0) == 0:
                skipped_zero += 1
                continue
            pending.append({'order_data': od, 'hub_id': hub_id, 'item_id': item_id})

        order_ids = {entry['order_data']['order_id'] for entry in pending}
        snapshot  = load_snapshot_for(order_ids)

        to_insert, full_updates, loc_fills, touch_only_pks, sf_data = classify_orders(
            pending, snapshot
        )
        apply_batch(to_insert, full_updates, loc_fills, touch_only_pks, sf_data)
        db.session.commit()

        n_created = len(to_insert)
        n_updated = len(full_updates) + len(loc_fills)
        n_touched = len(touch_only_pks)
        created       += n_created
        updated       += n_updated
        touched       += n_touched
        sales_created += len(sf_data)
        logger.debug('%s: +%d new  ~%d updated  =%d unchanged  (%d pending)',
                     region.name, n_created, n_updated, n_touched, len(pending))

    now = datetime.utcnow()
    sales_created += record_sold_out_orders(now)

    deleted_q = PublicTradeOrder.query.filter(PublicTradeOrder.touched.is_(False))
    deleted   = deleted_q.count()
    deleted_q.delete()

    db.session.commit()

    elapsed = time.perf_counter() - t0
    logger.info(
        'Done in %.1fs — +%d created ~%d updated =%d unchanged -%d deleted | '
        '%d sales recorded | skipped: %d no-hub  %d zero-volume',
        elapsed, created, updated, touched, deleted, sales_created,
        skipped_no_hub, skipped_zero,
    )
