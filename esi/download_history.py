import json
import os
import multiprocessing
from datetime import datetime, timedelta

from esi.client import EsiClient
from esi.errors import NotFound


PROCESSES_COUNT = 4


class DownloadHistory:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def download(self):
        from evebs.models import UniverseRegion
        os.makedirs('data', exist_ok=True)

        regions = UniverseRegion.query.all()
        chunk_size = max(1, len(regions) // PROCESSES_COUNT)
        chunks = [regions[i:i + chunk_size] for i in range(0, len(regions), chunk_size)]

        processes = []
        for i, chunk in enumerate(chunks, 1):
            region_ids = [r.id for r in chunk]
            p = multiprocessing.Process(target=_download_chunk, args=(region_ids, i, self.verbose))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        print('Download regional sales volumes finished')


def _download_chunk(region_ids, process_number, verbose):
    from run import app
    with app.app_context():
        from evebs.models import UniverseRegion
        regions = UniverseRegion.query.filter(UniverseRegion.id.in_(region_ids)).all()

    cutoff = datetime.utcnow() - timedelta(days=30)
    outfile = f'data/regional_sales_volumes_{process_number}.json_stream'

    with open(outfile, 'w') as f:
        for region in regions:
            if verbose:
                print(f'[{process_number}] Processing {region.name}')

            client = EsiClient(f'markets/{region.id}/types/')
            try:
                type_ids = client.get_all_pages()
            except Exception as e:
                print(f'Error getting types for {region.name}: {e}')
                continue

            for type_id in type_ids:
                hist_client = EsiClient(f'markets/{region.id}/history/',
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
                    'region_id': region.id,
                    'cpp_type_id': type_id,
                    'volume': total_volume,
                    'min': min_price,
                    'max': max_price,
                    'avg': sum(avg_prices) / len(avg_prices),
                }
                f.write(json.dumps(record) + '\n')
