import logging
from datetime import datetime
from esi.client import EsiClient

logger = logging.getLogger(__name__)


class DownloadMyAssets:
    def update(self, user):
        if user.locked:
            logger.debug('%s is locked. Skipping.', user.name)
            return

        client = EsiClient(f'characters/{user.uid}/assets/')
        if not client.set_auth_token(user):
            return

        pages = client.get_all_pages()
        from evebs.models import BpcAsset, EveItem, UniverseStation
        from evebs.extensions import db

        BpcAsset.query.filter_by(user_id=user.id).update({'touched': False})
        db.session.flush()

        for asset in pages:
            type_id = asset.get('type_id')
            location_id = asset.get('location_id')
            qty = asset.get('quantity', 1)

            eve_item_id = EveItem.to_eve_item_id(type_id)
            if not eve_item_id:
                continue

            station = UniverseStation.query.filter_by(cpp_station_id=location_id).first()
            station_id = station.id if station else None

            bpc = BpcAsset.query.filter_by(
                user_id=user.id, eve_item_id=eve_item_id
            ).first()
            if bpc:
                bpc.quantity = qty
                bpc.universe_station_id = station_id
                bpc.touched = True
            else:
                bpc = BpcAsset(
                    user_id=user.id, eve_item_id=eve_item_id,
                    quantity=qty, universe_station_id=station_id, touched=True,
                )
                db.session.add(bpc)

        BpcAsset.query.filter_by(user_id=user.id, touched=False).delete()
        user.download_assets_running = False
        user.last_assets_download = datetime.utcnow()
        db.session.commit()
