"""Fetch industry cost indices per solar system from ESI and store on UniverseSystem."""
from esi.client import EsiClient
from evebs.extensions import db
from evebs.models import UniverseSystem


def update_universe_solar_system_costs():
    """Download /industry/systems/ and upsert cost_indices on matching UniverseSystem rows."""
    records = EsiClient('industry/systems/').get_all_pages()

    by_id = {r['solar_system_id']: r['cost_indices'] for r in records}

    systems = UniverseSystem.query.filter(
        UniverseSystem.id.in_(by_id.keys())
    ).all()

    for system in systems:
        system.cost_indices = by_id[system.id]

    db.session.commit()
    print(f'Updated cost indices for {len(systems)} systems.')


if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from run import app
    with app.app_context():
        update_universe_solar_system_costs()
