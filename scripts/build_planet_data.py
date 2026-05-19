#!/usr/bin/env python3
"""Extract planet and schematic data from raw JSONL into data/planet_advice_data.json.

Run once (or after an EVE static data update) to regenerate the file used by
evebs/engine/planetary.py.
"""
import json
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(BASE, 'data', 'eve_static_data')
OUT = os.path.join(BASE, 'data', 'planet_advice_data.json')


def load_schematics():
    schematics = []
    with open(os.path.join(STATIC, 'planetSchematics.jsonl')) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            inputs = [{'type_id': t['_key'], 'qty': t['quantity']} for t in rec['types'] if t['isInput']]
            output = next({'type_id': t['_key'], 'qty': t['quantity']} for t in rec['types'] if not t['isInput'])
            schematics.append({
                'id': rec['_key'],
                'name': rec['name']['en'],
                'cycle_time': rec['cycleTime'],
                'inputs': inputs,
                'output': output,
            })
    return schematics


def load_planets():
    planets_by_system = defaultdict(list)
    with open(os.path.join(STATIC, 'mapPlanets.jsonl')) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            system_id = rec.get('solarSystemID')
            if system_id is None:
                continue
            planets_by_system[str(system_id)].append({
                'id': rec['_key'],
                'type_id': rec.get('typeID'),
                'index': rec.get('celestialIndex', 0),
            })
    return dict(planets_by_system)


def main():
    print('Loading schematics...')
    schematics = load_schematics()
    print(f'  {len(schematics)} schematics')

    print('Loading planets...')
    planets_by_system = load_planets()
    planet_count = sum(len(v) for v in planets_by_system.values())
    print(f'  {planet_count} planets across {len(planets_by_system)} systems')

    data = {
        'schematics': schematics,
        'planets_by_system': planets_by_system,
    }

    with open(OUT, 'w') as f:
        json.dump(data, f, separators=(',', ':'))

    size_kb = os.path.getsize(OUT) // 1024
    print(f'Written to {OUT} ({size_kb} KB)')


if __name__ == '__main__':
    main()
