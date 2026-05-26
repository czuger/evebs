import json
import logging
import os
from datetime import datetime, timedelta

from esi.client import EsiClient
from esi.errors import NotFound

logger = logging.getLogger(__name__)


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
    def __init__(self, essentials=False):
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
            logger.info('[history] essentials mode: %s hub regions, %s ammo/charges types',
                        len(regions), len(ammo_ids))
        else:
            ammo_ids = None

        cutoff = datetime.utcnow() - timedelta(days=30)
        outfile = 'data/regional_sales_volumes.json_stream'

        total_regions = len(regions)
        total_types = 0
        total_records = 0

        logger.info('[history] %s regions to process, cutoff %s', total_regions, cutoff.date())

        with open(outfile, 'w') as f:
            for region_idx, region in enumerate(regions, 1):
                logger.debug('[history] [%s/%s] %s — fetching type list',
                             region_idx, total_regions, region.name)

                client = EsiClient(f'markets/{region.cpp_region_id}/types/')
                try:
                    type_ids = client.get_all_pages()
                except Exception as e:
                    logger.warning('[history] [%s/%s] %s — ERROR fetching types: %s',
                                   region_idx, total_regions, region.name, e)
                    continue

                if ammo_ids is not None:
                    type_ids = [t for t in type_ids if t in ammo_ids]

                region_type_count = len(type_ids)
                region_written = 0

                logger.debug('[history] [%s/%s] %s — %s types',
                             region_idx, total_regions, region.name, region_type_count)

                if not type_ids:
                    continue

                for type_idx, type_id in enumerate(type_ids, 1):
                    if type_idx % 100 == 0:
                        logger.debug('[history]   %s %s/%s types processed',
                                     region.name, type_idx, region_type_count)

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
                logger.debug('[history] [%s/%s] %s done — %s/%s types written',
                             region_idx, total_regions, region.name,
                             region_written, region_type_count)

        logger.info('[history] finished — %s regions, %s types scanned, %s records written to %s',
                    total_regions, total_types, total_records, outfile)
