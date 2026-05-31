import json
import logging
import os
from datetime import datetime

from evebs.extensions import db
from evebs.models import PublicTradeOrder, EveItem, UniverseSystem
from esi.download_public_orders.upsert import (
    load_snapshot_for, classify_orders, apply_batch, record_sold_out_orders,
)

logger = logging.getLogger(__name__)

_DATA_FILE = os.path.join('data', 'public_trades_orders.json_stream')


def run() -> None:
    if not os.path.exists(_DATA_FILE):
        logger.debug('update_public_orders: %s not found, skipping', _DATA_FILE)
        return

    hub_map = {
        us.cpp_system_id: us.id
        for us in UniverseSystem.query.filter_by(trade_hub=True).all()
    }
    item_map = {ei.id: ei.id for ei in EveItem.query.all()}

    PublicTradeOrder.query.update({'touched': False})
    db.session.flush()

    pending = []
    with open(_DATA_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            od = json.loads(line)
            item_id = item_map.get(od.get('type_id'))
            if item_id is None:
                continue
            hub_id = hub_map.get(od.get('system_id'))
            if not hub_id:
                continue
            if od.get('volume_remain', 0) == 0:
                continue
            pending.append({'order_data': od, 'hub_id': hub_id, 'item_id': item_id})

    order_ids = {entry['order_data']['order_id'] for entry in pending}
    snapshot = load_snapshot_for(order_ids)
    to_insert, full_updates, loc_fills, touch_only_pks, sf_data = classify_orders(
        pending, snapshot
    )
    apply_batch(to_insert, full_updates, loc_fills, touch_only_pks, sf_data)
    db.session.commit()

    now = datetime.utcnow()
    record_sold_out_orders(now)

    deleted_q = PublicTradeOrder.query.filter(PublicTradeOrder.touched.is_(False))
    deleted_q.delete()
    db.session.commit()

    logger.debug('update_public_orders: +%d new  %d sf  -%d deleted',
                 len(to_insert), len(sf_data), deleted_q.count() if False else 0)
