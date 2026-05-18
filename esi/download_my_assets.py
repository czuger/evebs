from datetime import datetime

from esi.client import EsiClient
from evebs.extensions import db
from evebs.models import BpcAsset, UniverseStation, User, UniverseType


def download_my_assets(user):
    """Sync the user's in-game assets from ESI into BpcAsset records."""
    if user.locked:
        print(f'{user.name} is locked. Skipping.')
        return

    client = EsiClient(f'characters/{user.uid}/assets/')
    if not client.set_auth_token(user):
        return

    pages = client.get_all_pages()

    BpcAsset.query.filter_by(user_id=user.id).update({'touched': False})
    db.session.flush()

    for asset in pages:
        type_id = asset.get('type_id')
        location_id = asset.get('location_id')
        qty = asset.get('quantity', 1)

        eve_item = db.session.get(UniverseType, type_id)

        if not eve_item:
            continue

        station = UniverseStation.query.filter_by(id=location_id).first()
        station_id = station.id if station else None

        bpc = BpcAsset.query.filter_by(
            user_id=user.id, eve_item_id=eve_item.id
        ).first()
        if bpc:
            bpc.quantity = qty
            bpc.universe_station_id = station_id
            bpc.touched = True
        else:
            bpc = BpcAsset(
                user_id=user.id, eve_item_id=eve_item.id,
                quantity=qty, universe_station_id=station_id, touched=True,
            )
            db.session.add(bpc)

    BpcAsset.query.filter_by(user_id=user.id, touched=False).delete()
    user.download_assets_running = False
    user.last_assets_download = datetime.utcnow()
    db.session.commit()


if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from run import app
    with app.app_context():
        for user in User.query.all():
            download_my_assets(user)
