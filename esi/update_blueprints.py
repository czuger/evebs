"""Read data/eve_static_data/blueprints.jsonl and reload Blueprint + BlueprintMaterial records."""
import json
import os

from evebs.extensions import db
from evebs.models import Blueprint, BlueprintMaterial, UniverseType

JSONL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'data', 'eve_static_data', 'blueprints.jsonl',
)


def update_blueprints():
    """Reload all manufacturing blueprints and their materials from the static data file."""
    known_type_ids = {r[0] for r in db.session.query(UniverseType.id).all()}
    type_names = {r[0]: r[1] for r in db.session.query(UniverseType.id, UniverseType.name).all()}

    BlueprintMaterial.query.delete()
    Blueprint.query.delete()
    db.session.flush()

    created = skipped = 0
    seen_produced_ids = set()

    with open(JSONL_PATH) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            manufacturing = record.get('activities', {}).get('manufacturing')
            if not manufacturing:
                skipped += 1
                continue

            products = manufacturing.get('products', [])
            if not products:
                skipped += 1
                continue

            blueprint_type_id = record['blueprintTypeID']
            produced_type_id = products[0]['typeID']
            prod_qtt = products[0].get('quantity', 1)
            materials = manufacturing.get('materials', [])

            if produced_type_id not in known_type_ids or produced_type_id in seen_produced_ids:
                skipped += 1
                continue

            seen_produced_ids.add(produced_type_id)
            name = type_names.get(produced_type_id, '')

            db.session.add(Blueprint(
                id=blueprint_type_id,
                produced_type_id=produced_type_id,
                prod_qtt=prod_qtt,
                nb_runs=1,
                name=name,
            ))

            for mat in materials:
                if mat['typeID'] not in known_type_ids:
                    continue
                db.session.add(BlueprintMaterial(
                    blueprint_id=blueprint_type_id,
                    universe_type_id=mat['typeID'],
                    required_qtt=mat['quantity'],
                ))

            created += 1

            if i % 500 == 0:
                db.session.flush()
                print(f'  {i} records processed (created={created}, skipped={skipped})...')

    db.session.commit()
    print(f'Done. Created: {created}, skipped: {skipped}.')


if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from run import app
    with app.app_context():
        update_blueprints()
