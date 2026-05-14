import yaml
import os
from esi.client import EsiClient


class DownloadMarketsPrices:
    def download(self):
        client = EsiClient('markets/prices/')
        prices = client.get_all_pages()

        price_map = {}
        for p in prices:
            price_map[p['type_id']] = {
                'adjusted_price': p.get('adjusted_price'),
                'average_price': p.get('average_price'),
            }

        os.makedirs('data', exist_ok=True)
        with open('data/cpp_market_prices.yaml', 'w') as f:
            yaml.dump(price_map, f)

        print(f'Downloaded {len(price_map)} market prices')
