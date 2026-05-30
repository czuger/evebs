import logging
import time

from esi.client import EsiClient
from esi.errors import NotFound

logger = logging.getLogger(__name__)


def fetch_region_types(region) -> set[int]:
    client = EsiClient(f'markets/{region.cpp_region_id}/types/')
    try:
        type_ids = client.get_all_pages()
    except NotFound:
        logger.warning('NotFound for region %s types — retrying in 60s', region.name)
        time.sleep(60)
        type_ids = client.get_all_pages()
    return set(type_ids)


def fetch_type_orders(region, type_id: int) -> list[dict]:
    client = EsiClient(f'markets/{region.cpp_region_id}/orders/', params={'type_id': type_id})
    try:
        return client.get_all_pages()
    except NotFound:
        logger.warning('NotFound for region %s type %d — retrying in 60s', region.name, type_id)
        time.sleep(60)
        return client.get_all_pages()


def fetch_region_all_orders(region) -> list[dict]:
    client  = EsiClient(f'markets/{region.cpp_region_id}/orders/')
    page    = 1
    result  = []
    t_start = time.perf_counter()
    t_page  = t_start
    while True:
        try:
            page_data = client.get_page(page)
        except NotFound:
            logger.warning('NotFound for region %s all-orders page %d — retrying in 60s',
                           region.name, page)
            time.sleep(60)
            page_data = client.get_page(page)

        total = client._pages_count or 1
        if isinstance(page_data, list):
            result.extend(page_data)
        now     = time.perf_counter()
        page_ms = (now - t_page) * 1000
        total_s = now - t_start
        t_page  = now
        logger.info('[%s] page %d/%d — %d orders fetched — page %.0fms  total %.1fs',
                    region.name, page, total, len(result), page_ms, total_s)

        if total <= 1 or page >= total:
            break
        page += 1

    logger.info('[%s] fetch complete: %d orders in %.1fs',
                region.name, len(result), time.perf_counter() - t_start)
    return result
