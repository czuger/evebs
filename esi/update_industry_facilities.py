"""Fetch all industry-capable facilities from ESI and replace the industry_facilities table."""
from esi.client import EsiClient
from evebs.extensions import db
from evebs.models import IndustryFacility, UniverseStation


def update_industry_facilities():
    """Download /industry/facilities/ and replace all IndustryFacility rows."""
    records = EsiClient('industry/facilities/').get_all_pages()

    known_station_ids = {
        row.id for row in db.session.query(UniverseStation.id).all()
    }

    IndustryFacility.query.delete()

    facilities = []
    for r in records:
        facility_id = r['facility_id']
        facilities.append(IndustryFacility(
            id=facility_id,
            universe_system_id=r['solar_system_id'],
            universe_station_id=facility_id if facility_id in known_station_ids else None,
            owner_id=r['owner_id'],
            type_id=r['type_id'],
            tax=r.get('tax'),
        ))

    db.session.bulk_save_objects(facilities)
    db.session.commit()
    print(f'Replaced industry_facilities with {len(facilities)} records.')


if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from run import app
    with app.app_context():
        update_industry_facilities()
