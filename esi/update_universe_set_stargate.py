"""Fetch full stargate details from ESI and store them in universe_systems.stargates."""
import json
import os
from esi.client import EsiClient
from evebs.extensions import db
from evebs.models import UniverseSystem


def update_universe_set_stargate():
    systems = UniverseSystem.query.all()
    total = len(systems)
    print(f'Fetching stargates for {total} systems...')

    updated = skipped = 0
    for i, system in enumerate(systems, 1):
        print(f'[{i}/{total}] Fetching system {system.id} ({system.name})...')
        system_detail = EsiClient(f'universe/systems/{system.id}/').get_page()
        if not system_detail:
            print(f'  -> no data, skipping')
            skipped += 1
            continue

        stargate_ids = system_detail.get('stargates', [])
        stargate_details = []
        for sg_id in stargate_ids:
            print(f'  -> stargate {sg_id}')
            detail = EsiClient(f'universe/stargates/{sg_id}/').get_page()
            if detail:
                stargate_details.append(detail)

        system.stargates = stargate_details
        updated += 1

        if i % 100 == 0:
            db.session.flush()

    db.session.commit()
    print(f'Done. Updated: {updated}, skipped: {skipped}.')

    _build_graph(systems)


def _build_graph(systems):
    id_to_name = {s.id: s.name for s in systems}
    graph = {}
    for system in systems:
        if not system.stargates:
            continue
        neighbors = []
        for sg in system.stargates:
            dest_system_id = sg.get('destination', {}).get('system_id')
            name = id_to_name.get(dest_system_id)
            if name:
                neighbors.append(name)
        if neighbors:
            graph[system.name] = {
                'security': round(system.security_status, 1),
                'neighbors': neighbors,
            }

    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'universe_graph.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(graph, f)
    print(f'Graph written to {out_path} ({len(graph)} systems).')


if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from run import app
    with app.app_context():
        update_universe_set_stargate()
