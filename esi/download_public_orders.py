import csv
import json
import os
import sys
import time
from datetime import datetime, timedelta
from esi.client import EsiClient
from esi.errors import NotFound

BATCH_SIZE = 500


class DownloadPublicTradesOrders:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def download(self):
        from evebs.models import TradeHub, EveItem, UniverseRegion, UniverseSystem

        trade_hub_ids = set(row[0] for row in TradeHub.query.with_entities(TradeHub.eve_system_id).all())
        eve_item_ids = set(row[0] for row in EveItem.query.with_entities(EveItem.cpp_eve_item_id).all())
        systems_to_name = {r[0]: r[1] for r in UniverseSystem.query.with_entities(
            UniverseSystem.cpp_system_id, UniverseSystem.name).all()}

        if self.verbose:
            print(f'Trade hub count = {len(trade_hub_ids)}, items count = {len(eve_item_ids)}')

        os.makedirs('data', exist_ok=True)
        rejected_by_hub = {}
        rejected_by_type = {}

        with open('data/public_trades_orders.json_stream', 'w') as f:
            for region in UniverseRegion.query.all():
                if self.verbose:
                    print(f'Downloading orders for {region.name}')

                client = EsiClient(f'markets/{region.cpp_region_id}/orders/',
                                   verbose=self.verbose)
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

        if self.verbose:
            print(f'Download complete. Rejected by hub: {len(rejected_by_hub)}, by type: {len(rejected_by_type)}')

    def load_from_csv(self, filepath):
        from evebs.extensions import db
        from evebs.models import TradeHub, EveItem, PublicTradeOrder

        t0 = time.perf_counter()
        print(f'Loading orders from: {filepath}')
        sys.stdout.flush()

        print('  loading reference data…', end=' ', flush=True)
        hub_map  = {th.eve_system_id: th.id for th in TradeHub.query.all()}
        item_map = {ei.cpp_eve_item_id: ei.id for ei in EveItem.query.all()}
        existing = {o.order_id: o for o in PublicTradeOrder.query.all()}
        print(f'{len(hub_map):,} hubs  |  {len(item_map):,} items  |  {len(existing):,} existing orders')
        sys.stdout.flush()

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
                    if self.verbose:
                        elapsed = time.perf_counter() - t0
                        total_skipped = skipped_zero + skipped_no_hub + skipped_no_item
                        print(f'  … {batch:,} rows  |  +{created:,} new  ~{updated:,} updated'
                              f'  |  {total_skipped:,} skipped  |  {elapsed:.1f}s')
                        sys.stdout.flush()

        db.session.commit()
        elapsed = time.perf_counter() - t0
        total_read = batch + skipped_zero + skipped_no_hub + skipped_no_item
        print(
            f'  done in {elapsed:.1f}s  —  {total_read:,} rows read\n'
            f'  PublicTradeOrder: {created:,} created  |  {updated:,} updated\n'
            f'  skipped: {skipped_zero:,} zero-volume  |  '
            f'{skipped_no_hub:,} unknown hub  |  {skipped_no_item:,} unknown item'
        )
        sys.stdout.flush()
