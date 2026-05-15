from esi.client import EsiClient


def download_universe_regions():
    client = EsiClient('universe/regions/')
    region_ids = client.get_all_pages()

    from evebs.models import UniverseRegion
    from evebs.extensions import db

    for region_id in region_ids:
        detail_client = EsiClient(f'universe/regions/{region_id}/')
        data = detail_client.get_page()
        if not data:
            continue

        region = UniverseRegion.query.filter_by(cpp_region_id=region_id).first()
        if not region:
            region = UniverseRegion(cpp_region_id=region_id, name=data.get('name', ''))
            db.session.add(region)
        else:
            region.name = data.get('name', region.name)

    db.session.commit()
    print('Universe regions download complete')


if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from run import app
    with app.app_context():
        download_universe_regions()
