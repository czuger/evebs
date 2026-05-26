import csv
import json
import logging
import os
import time
from datetime import datetime, timedelta
from esi.client import EsiClient
from esi.errors import NotFound

logger = logging.getLogger(__name__)

BATCH_SIZE = 500


class DownloadPublicTradesOrders:
    def __init__(self, essentials=False):
        self.essentials = essentials

    def download(self):
        from evebs.models import TradeHub, EveItem, UniverseRegion, UniverseSystem

        trade_hub_ids = set(row[0] for row in TradeHub.query.with_entities(TradeHub.eve_system_id).all())
        eve_item_ids = set(row[0] for row in EveItem.query.with_entities(EveItem.cpp_eve_item_id).all())
        systems_to_name = {r[0]: r[1] for r in UniverseSystem.query.with_entities(
            UniverseSystem.cpp_system_id, UniverseSystem.name).all()}

        regions = UniverseRegion.query.all()

        if self.essentials:
            from esi.download_history import _ammo_market_group_ids
            hub_cpp_ids = {int(th.region.cpp_region_id) for th in TradeHub.query.all() if th.region}
            regions = [r for r in regions if r.cpp_region_id in hub_cpp_ids]
            ammo_group_ids = _ammo_market_group_ids()
            ammo_cpp_ids = {
                item.cpp_eve_item_id
                for item in EveItem.query.filter(EveItem.market_group_id.in_(ammo_group_ids)).all()
            }
            eve_item_ids = eve_item_ids & ammo_cpp_ids
            logger.info('[orders] essentials mode: %s hub regions, %s ammo/charges types',
                        len(regions), len(eve_item_ids))

        logger.debug('Trade hub count = %s, items count = %s', len(trade_hub_ids), len(eve_item_ids))

        os.makedirs('data', exist_ok=True)
        rejected_by_hub = {}
        rejected_by_type = {}

        with open('data/public_trades_orders.json_stream', 'w') as f:
            for region in regions:
                logger.debug('Downloading orders for %s', region.name)

                client = EsiClient(f'markets/{region.cpp_region_id}/orders/')
                try:
                    orders_data = client.get_all_pages()
                except NotFound:
                    import time; time.sleep(60)
                    orders_data = client.get_all_pages()

                seen = {}
                for order in orders_data:
                    oid = order['order_id']
                    if oid not in seen:
                        seen[oid] = order

                for order in seen.values():
                    system_id = order.get('system_id')
                    type_id = order.get('type_id')

                    if system_id not in trade_hub_ids:
                        key = systems_to_name.get(system_id, str(system_id))
                        rejected_by_hub[key] = rejected_by_hub.get(key, 0) + 1
                        continue

                    if type_id not in eve_item_ids:
                        rejected_by_type[type_id] = rejected_by_type.get(type_id, 0) + 1
                        continue

                    if order.get('volume_remain', 0) == 0:
                        continue

                    f.write(json.dumps(order) + '\n')

        logger.info('Download complete. Rejected by hub: %s, by type: %s',
                    len(rejected_by_hub), len(rejected_by_type))

    def load_from_csv(self, filepath):
        from evebs.extensions import db
        from evebs.models import TradeHub, EveItem, PublicTradeOrder

        t0 = time.perf_counter()
        logger.info('Loading orders from: %s', filepath)

        logger.debug('loading reference data')
        hub_map  = {th.eve_system_id: th.id for th in TradeHub.query.all()}
        item_map = {ei.cpp_eve_item_id: ei.id for ei in EveItem.query.all()}
        existing = {o.order_id: o for o in PublicTradeOrder.query.all()}
        logger.debug('%s hubs  |  %s items  |  %s existing orders',
                     len(hub_map), len(item_map), len(existing))

        created = updated = 0
        skipped_zero   = 0
        skipped_no_hub = 0
        skipped_no_item = 0
        batch = 0

        with open(filepath, newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                volume_remain = int(row['volume_remain'])
                if volume_remain == 0:
                    skipped_zero += 1
                    continue

                system_id = int(row['system_id'])
                type_id   = int(row['type_id'])
                hub_id    = hub_map.get(system_id)
                item_id   = item_map.get(type_id)

                if hub_id is None:
                    skipped_no_hub += 1
                    continue
                if item_id is None:
                    skipped_no_item += 1
                    continue

                order_id = int(row['id'])
                end_time = datetime.fromisoformat(row['issued']) + timedelta(days=int(row['duration']))
                is_buy   = row['is_buy_order'].strip().lower() in ('t', 'true', '1')

                o = existing.get(order_id)
                if o:
                    o.trade_hub_id  = hub_id
                    o.eve_item_id   = item_id
                    o.is_buy_order  = is_buy
                    o.end_time      = end_time
                    o.price         = float(row['price'])
                    o.range         = row['range']
                    o.volume_remain = volume_remain
                    o.volume_total  = int(row['volume_total'])
                    o.min_volume    = int(row['min_volume'])
                    updated += 1
                else:
                    db.session.add(PublicTradeOrder(
                        order_id      = order_id,
                        trade_hub_id  = hub_id,
                        eve_item_id   = item_id,
                        is_buy_order  = is_buy,
                        end_time      = end_time,
                        price         = float(row['price']),
                        range         = row['range'],
                        volume_remain = volume_remain,
                        volume_total  = int(row['volume_total']),
                        min_volume    = int(row['min_volume']),
                    ))
                    created += 1

                batch += 1
                if batch % BATCH_SIZE == 0:
                    db.session.commit()
                    elapsed = time.perf_counter() - t0
                    total_skipped = skipped_zero + skipped_no_hub + skipped_no_item
                    logger.debug('  … %s rows  |  +%s new  ~%s updated  |  %s skipped  |  %.1fs',
                                 batch, created, updated, total_skipped, elapsed)

        db.session.commit()
        elapsed = time.perf_counter() - t0
        total_read = batch + skipped_zero + skipped_no_hub + skipped_no_item
        logger.info(
            '  done in %.1fs  —  %s rows read; PublicTradeOrder: %s created  |  %s updated; '
            'skipped: %s zero-volume  |  %s unknown hub  |  %s unknown item',
            elapsed, total_read, created, updated, skipped_zero, skipped_no_hub, skipped_no_item
        )
