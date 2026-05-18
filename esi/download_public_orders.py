"""This is legacy"""
import json
import os
from esi.client import EsiClient
from esi.errors import NotFound


class DownloadPublicTradesOrders:
    """Legacy downloader: fetches all region orders and writes a JSON-stream file."""

    def __init__(self, verbose=False):
        self.verbose = verbose

    def download(self):
        """Download all public orders across regions and write matching ones to disk."""
        from evebs.models import TradeHub, UniverseType, UniverseRegion, UniverseSystem

        trade_hub_ids = set(row[0] for row in TradeHub.query.with_entities(TradeHub.eve_system_id).all())
        eve_item_ids = set(row[0] for row in UniverseType.query.with_entities(UniverseType.id).all())
        systems_to_name = {r[0]: r[1] for r in UniverseSystem.query.with_entities(
            UniverseSystem.id, UniverseSystem.name).all()}

        if self.verbose:
            print(f'Trade hub count = {len(trade_hub_ids)}, items count = {len(eve_item_ids)}')

        os.makedirs('data', exist_ok=True)
        rejected_by_hub = {}
        rejected_by_type = {}

        with open('data/public_trades_orders.json_stream', 'w') as f:
            for region in UniverseRegion.query.all():
                if self.verbose:
                    print(f'Downloading orders for {region.name}')

                client = EsiClient(f'markets/{region.id}/orders/',
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
