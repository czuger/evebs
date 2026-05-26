import logging
import yaml
import os
from esi.client import EsiClient

logger = logging.getLogger(__name__)


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

        logger.debug('Downloaded %s market prices', len(price_map))
