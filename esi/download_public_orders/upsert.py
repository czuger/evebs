import logging
from datetime import datetime, timedelta

from sqlalchemy import insert, update, select

from evebs.extensions import db
from evebs.models import PublicTradeOrder, SalesFinal

logger = logging.getLogger(__name__)

_TOUCH_CHUNK = 10_000


def load_snapshot_for(order_ids: set[int]) -> dict[int, dict]:
    """Return {order_id: row} for the given order_ids only."""
    if not order_ids:
        return {}
    rows = db.session.execute(
        select(
            PublicTradeOrder.id,
            PublicTradeOrder.order_id,
            PublicTradeOrder.volume_remain,
            PublicTradeOrder.price,
            PublicTradeOrder.end_time,
            PublicTradeOrder.location_id,
        ).where(PublicTradeOrder.order_id.in_(order_ids))
    ).mappings()
    return {r['order_id']: dict(r) for r in rows}


def classify_orders(
    pending: list[dict],
    snapshot: dict[int, dict],
) -> tuple[list[dict], list[dict], list[dict], list[int], list[dict]]:
    """Split pending ESI orders into DB operation buckets.

    pending items: {'order_data': ..., 'hub_id': ..., 'item_id': ...}

    Returns (to_insert, full_updates, loc_fills, touch_only_pks, sales_finals):
      to_insert       — dicts for new rows (bulk INSERT)
      full_updates    — {id, volume_remain, price, end_time, location_id, touched}
      loc_fills       — {id, location_id, touched} for unchanged rows needing location set
      touch_only_pks  — internal PKs for unchanged rows needing only touched=True
      sales_finals    — dicts for SalesFinal bulk INSERT
    """
    to_insert      = []
    full_updates   = []
    loc_fills      = []
    touch_only_pks = []
    sales_finals   = []
    now_date       = datetime.utcnow().date()

    for entry in pending:
        od       = entry['order_data']
        hub_id   = entry['hub_id']
        item_id  = entry['item_id']
        issued   = datetime.strptime(od['issued'][:19], '%Y-%m-%dT%H:%M:%S')
        end_time = issued + timedelta(days=od.get('duration', 0))
        order_id = od['order_id']
        vol      = od['volume_remain']
        price    = od['price']
        loc      = od.get('location_id')

        ex = snapshot.get(order_id)
        if ex is None:
            to_insert.append({
                'order_id':      order_id,
                'trade_hub_id':  hub_id,
                'eve_item_id':   item_id,
                'is_buy_order':  od.get('is_buy_order', False),
                'end_time':      end_time,
                'price':         price,
                'range':         od.get('range', 'station'),
                'volume_remain': vol,
                'volume_total':  od.get('volume_total', vol),
                'min_volume':    od.get('min_volume', 1),
                'location_id':   loc,
                'touched':       True,
            })
        else:
            changed = (
                ex['volume_remain'] != vol
                or ex['price'] != price
                or ex['end_time'] != end_time
            )
            if changed:
                if not od.get('is_buy_order') and ex['volume_remain'] > vol:
                    sales_finals.append({
                        'day':          now_date,
                        'trade_hub_id': hub_id,
                        'eve_item_id':  item_id,
                        'volume':       ex['volume_remain'] - vol,
                        'price':        price,
                        'order_id':     order_id,
                    })
                full_updates.append({
                    'id':            ex['id'],
                    'volume_remain': vol,
                    'price':         price,
                    'end_time':      end_time,
                    'location_id':   ex['location_id'] or loc,
                    'touched':       True,
                })
            elif ex['location_id'] is None and loc is not None:
                loc_fills.append({'id': ex['id'], 'location_id': loc, 'touched': True})
            else:
                touch_only_pks.append(ex['id'])

    return to_insert, full_updates, loc_fills, touch_only_pks, sales_finals


def apply_batch(
    to_insert:      list[dict],
    full_updates:   list[dict],
    loc_fills:      list[dict],
    touch_only_pks: list[int],
    sales_finals:   list[dict],
) -> None:
    """Execute all bulk DB operations for one classified batch."""
    if to_insert:
        db.session.execute(insert(PublicTradeOrder), to_insert)
    if full_updates:
        db.session.execute(update(PublicTradeOrder), full_updates)
    if loc_fills:
        db.session.execute(update(PublicTradeOrder), loc_fills)
    if touch_only_pks:
        for i in range(0, len(touch_only_pks), _TOUCH_CHUNK):
            db.session.execute(
                update(PublicTradeOrder)
                .where(PublicTradeOrder.id.in_(touch_only_pks[i:i + _TOUCH_CHUNK]))
                .values(touched=True)
            )
    if sales_finals:
        db.session.execute(insert(SalesFinal), sales_finals)


def flush_expired_orders(now: datetime) -> int:
    """Bulk-insert SalesFinal for expired untouched sell orders; return count."""
    rows = db.session.execute(
        select(
            PublicTradeOrder.order_id,
            PublicTradeOrder.trade_hub_id,
            PublicTradeOrder.eve_item_id,
            PublicTradeOrder.volume_remain,
            PublicTradeOrder.price,
        ).where(
            PublicTradeOrder.touched.is_(False),
            PublicTradeOrder.is_buy_order.is_(False),
            PublicTradeOrder.end_time < now,
        )
    ).mappings().all()

    if rows:
        db.session.execute(insert(SalesFinal), [
            {
                'day':          now.date(),
                'trade_hub_id': r['trade_hub_id'],
                'eve_item_id':  r['eve_item_id'],
                'volume':       r['volume_remain'],
                'price':        r['price'],
                'order_id':     r['order_id'],
            }
            for r in rows
        ])

    logger.debug('%d expired orders → sales_finals', len(rows))
    return len(rows)
