import json
import os
from datetime import datetime, timedelta

from esi.client import EsiClient
from esi.errors import NotFound


def _ammo_market_group_ids():
    from evebs.models import MarketGroup
    all_groups = MarketGroup.query.all()
    children_map = {}
    for g in all_groups:
        children_map.setdefault(g.id, [])
        if g.parent_id is not None:
            children_map.setdefault(g.parent_id, []).append(g.id)

    roots = [g.id for g in all_groups if g.name and 'Ammunition' in g.name and g.parent_id is None]

    result = set()
    stack = list(roots)
    while stack:
        gid = stack.pop()
        result.add(gid)
        stack.extend(children_map.get(gid, []))
    return result


class DownloadHistory:
    def __init__(self, verbose=False, essentials=False):
        self.verbose = verbose
        self.essentials = essentials

    def download(self):
        from evebs.models import UniverseRegion
        os.makedirs('data', exist_ok=True)

        regions = UniverseRegion.query.all()

        if self.essentials:
            from evebs.models import TradeHub, EveItem
            hub_cpp_ids = {
                int(th.region.cpp_region_id)
                for th in TradeHub.query.all()
                if th.region
            }
            regions = [r for r in regions if r.cpp_region_id in hub_cpp_ids]
            ammo_group_ids = _ammo_market_group_ids()
            ammo_ids = {
                item.cpp_eve_item_id
                for item in EveItem.query.filter(
                    EveItem.market_group_id.in_(ammo_group_ids)
                ).all()
            }
            print(f'[history] essentials mode: {len(regions)} hub regions, {len(ammo_ids)} ammo/charges types')
        else:
            ammo_ids = None

        cutoff = datetime.utcnow() - timedelta(days=30)
        outfile = 'data/regional_sales_volumes.json_stream'

        total_regions = len(regions)
        total_types = 0
        total_records = 0

        print(f'[history] {total_regions} regions to process, cutoff {cutoff.date()}')

        with open(outfile, 'w') as f:
            for region_idx, region in enumerate(regions, 1):
                if self.verbose:
                    print(f'[history] [{region_idx}/{total_regions}] {region.name} — fetching type list')

                client = EsiClient(f'markets/{region.cpp_region_id}/types/')
                try:
                    type_ids = client.get_all_pages()
                except Exception as e:
                    print(f'[history] [{region_idx}/{total_regions}] {region.name} — ERROR fetching types: {e}')
                    continue

                if ammo_ids is not None:
                    type_ids = [t for t in type_ids if t in ammo_ids]

                region_type_count = len(type_ids)
                region_written = 0

                if self.verbose:
                    print(f'[history] [{region_idx}/{total_regions}] {region.name} — {region_type_count} types')

                if not type_ids:
                    continue

                for type_idx, type_id in enumerate(type_ids, 1):
                    if self.verbose and type_idx % 100 == 0:
                        print(f'[history]   {region.name} {type_idx}/{region_type_count} types processed')

                    hist_client = EsiClient(f'markets/{region.cpp_region_id}/history/',
                                            params={'type_id': type_id})
                    try:
                        records = hist_client.get_all_pages()
                    except NotFound:
                        continue

                    total_volume = 0
                    total_isk = 0.0
                    avg_prices = []
                    min_price = None
                    max_price = None

                    for rec in records:
                        try:
                            rec_date = datetime.strptime(rec['date'], '%Y-%m-%d')
                        except (KeyError, ValueError):
                            continue
                        if rec_date < cutoff:
                            continue

                        vol = int(rec.get('volume', 0))
                        avg = float(rec.get('average', 0))
                        total_volume += vol
                        total_isk += vol * avg
                        avg_prices.append(avg)
                        lo = float(rec.get('lowest', 0))
                        hi = float(rec.get('highest', 0))
                        min_price = lo if min_price is None else min(lo, min_price)
                        max_price = hi if max_price is None else max(hi, max_price)

                    if not avg_prices:
                        continue

                    record = {
                        'cpp_region_id': region.cpp_region_id,
                        'cpp_type_id': type_id,
                        'volume': total_volume,
                        'min': min_price,
                        'max': max_price,
                        'avg': sum(avg_prices) / len(avg_prices),
                    }
                    f.write(json.dumps(record) + '\n')
                    region_written += 1

                total_types += region_type_count
                total_records += region_written
                print(f'[history] [{region_idx}/{total_regions}] {region.name} done — '
                      f'{region_written}/{region_type_count} types written')

        print(f'[history] finished — {total_regions} regions, {total_types} types scanned, '
              f'{total_records} records written to {outfile}')
