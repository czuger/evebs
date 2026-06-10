import logging

from esi.client import EsiClient
from evebs.extensions import db
from evebs.models import UniverseRegion

logger = logging.getLogger(__name__)


class DownloadUniverseRegions:
    def download(self):
        client = EsiClient('universe/regions/')
        region_ids = client.get_all_pages()

        for region_id in region_ids:
            detail_client = EsiClient(f'universe/regions/{region_id}/')
            data = detail_client.get_page()
            if not data:
                continue

            region = UniverseRegion.query.get(region_id)
            if not region:
                region = UniverseRegion(id=region_id, name=data.get('name', ''))
                db.session.add(region)
            else:
                region.name = data.get('name', region.name)

        db.session.commit()
        logger.debug('Universe regions download complete')
