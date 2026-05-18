"""Process downloaded public_trades_orders.json_stream into the database."""
import json
from datetime import datetime, timedelta

from evebs.extensions import db
from evebs.models import PublicTradeOrder, TradeHub, UniverseType, SalesFinal


def run(verbose=False):
    """Process the public trades JSON-stream into PublicTradeOrder and SalesFinal records."""
    print('Updating public trade orders...')

    trade_hub_map = {r[0]: r[1] for r in TradeHub.query.with_entities(
        TradeHub.eve_system_id, TradeHub.id).all()}
    item_map = {r[0]: r[0] for r in UniverseType.query.with_entities(UniverseType.id).all()}

    PublicTradeOrder.query.update({'touched': False})
    db.session.flush()

    created = updated = touched = deleted = 0
    sales_created = 0

    try:
        f = open('data/public_trades_orders.json_stream', 'r')
    except FileNotFoundError:
        print('No orders file found, skipping.')
        return

    with f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                order_data = json.loads(line)
            except json.JSONDecodeError:
                continue

            system_id = order_data.get('system_id')
            type_id = order_data.get('type_id')
            trade_hub_id = trade_hub_map.get(system_id)
            eve_item_id = item_map.get(type_id)

            if not trade_hub_id or not eve_item_id:
                continue

            if order_data.get('volume_remain', 0) == 0:
                continue

            issued = datetime.strptime(order_data['issued'][:19], '%Y-%m-%dT%H:%M:%S')
            end_time = issued + timedelta(days=order_data.get('duration', 0))

            existing = PublicTradeOrder.query.filter_by(
                order_id=order_data['order_id']).first()

            if existing:
                changed = (existing.volume_remain != order_data['volume_remain'] or
                           existing.price != order_data['price'] or
                           existing.end_time != end_time)
                if changed:
                    if not order_data.get('is_buy_order'):
                        if existing.volume_remain != order_data['volume_remain']:
                            vol_sold = existing.volume_remain - order_data['volume_remain']
                            if vol_sold > 0:
                                sf = SalesFinal(
                                    day=datetime.utcnow().date(),
                                    trade_hub_id=existing.trade_hub_id,
                                    eve_item_id=existing.eve_item_id,
                                    volume=vol_sold,
                                    price=order_data['price'],
                                    order_id=existing.order_id,
                                )
                                db.session.add(sf)
                                sales_created += 1

                    existing.volume_remain = order_data['volume_remain']
                    existing.price = order_data['price']
                    existing.end_time = end_time
                    existing.touched = True
                    updated += 1
                else:
                    existing.touched = True
                    touched += 1
            else:
                new_order = PublicTradeOrder(
                    order_id=order_data['order_id'],
                    trade_hub_id=trade_hub_id,
                    eve_item_id=eve_item_id,
                    is_buy_order=order_data.get('is_buy_order', False),
                    end_time=end_time,
                    price=order_data['price'],
                    range=order_data.get('range', 'station'),
                    volume_remain=order_data['volume_remain'],
                    volume_total=order_data.get('volume_total', order_data['volume_remain']),
                    min_volume=order_data.get('min_volume', 1),
                    touched=True,
                )
                db.session.add(new_order)
                created += 1

    # Mark expired untouched sell orders as sold
    now = datetime.utcnow()
    expired = PublicTradeOrder.query.filter(
        PublicTradeOrder.touched.is_(False),
        PublicTradeOrder.is_buy_order.is_(False),
        PublicTradeOrder.end_time < now,
    ).all()
    for old in expired:
        sf = SalesFinal(
            day=now.date(),
            trade_hub_id=old.trade_hub_id,
            eve_item_id=old.eve_item_id,
            volume=old.volume_remain,
            price=old.price,
            order_id=old.order_id,
        )
        db.session.add(sf)
        sales_created += 1

    deleted_q = PublicTradeOrder.query.filter(PublicTradeOrder.touched.is_(False))
    deleted = deleted_q.count()
    deleted_q.delete()

    db.session.commit()

    if verbose:
        print(f'Created: {created}, Updated: {updated}, Touched: {touched}, '
              f'Deleted: {deleted}, Sales: {sales_created}')
    print('Public trade orders update complete.')
