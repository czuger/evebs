"""Planetary industry advice engine.

Loads planet and schematic data from data/planet_advice_data.json at module
import (same pattern as routing.py / universe_graph.json) and exposes
get_planetary_advice() for the route layer.
"""
import json
import os

from evebs.engine.routing import find_systems_within_jumps

_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'data', 'planet_advice_data.json',
)

with open(_DATA_PATH) as _f:
    _DATA = json.load(_f)

_SCHEMATICS = _DATA['schematics']
_PLANETS_BY_SYSTEM = _DATA['planets_by_system']

# Planet typeID → set of extractable P0 resource type IDs (stable EVE game data)
_PLANET_RESOURCES = {
    11:   {2268, 2305, 2267, 2288, 2287, 2272, 2073, 2310, 2270},  # Temperate
    2016: {2268, 2267, 2272, 2310, 2270, 2306, 2308},              # Barren
    2063: {2268, 2288, 2287, 2272, 2309, 2073, 2286},              # Oceanic
    2014: {2268, 2272, 2309, 2310, 2306, 2286},                    # Ice
    13:   {2268, 2305, 2288, 2287, 2309, 2073, 2310, 2286, 2311},  # Gas/Storm
    2015: {2307, 2272, 2306, 2311, 2308},                          # Lava
    2017: {2267, 2307, 2272, 2310, 2270, 2306, 2311, 2308},        # Plasma
}

PLANET_TYPE_NAMES = {
    11:   'Temperate',
    2016: 'Barren',
    2063: 'Oceanic',
    2014: 'Ice',
    13:   'Gas/Storm',
    2015: 'Lava',
    2017: 'Plasma',
}


def _build_p2_schematics():
    """Return enriched P2 schematic dicts with viable planet types and P1 names.

    Identifies P2 schematics structurally (inputs are all outputs of P1
    schematics) without hardcoding type IDs.
    """
    output_to_sch = {s['output']['type_id']: s for s in _SCHEMATICS}

    all_output_ids = set(output_to_sch)
    all_input_ids = {inp['type_id'] for s in _SCHEMATICS for inp in s['inputs']}
    p0_ids = all_input_ids - all_output_ids

    p1_ids = {
        s['output']['type_id']
        for s in _SCHEMATICS
        if all(inp['type_id'] in p0_ids for inp in s['inputs'])
    }

    p2 = []
    for s in _SCHEMATICS:
        if not all(inp['type_id'] in p1_ids for inp in s['inputs']):
            continue

        p0_type_ids = set()
        p1_names = []
        for p1_inp in s['inputs']:
            p1_sch = output_to_sch.get(p1_inp['type_id'])
            if p1_sch:
                p1_names.append(p1_sch['name'])
                for p0_inp in p1_sch['inputs']:
                    p0_type_ids.add(p0_inp['type_id'])

        viable = [
            pt for pt, resources in _PLANET_RESOURCES.items()
            if p0_type_ids.issubset(resources)
        ]

        p2.append({
            **s,
            'viable_planet_types': viable,
            'p1_names': p1_names,
        })

    return p2


P2_SCHEMATICS = _build_p2_schematics()


def get_planetary_advice(origin_system_name, max_jumps, avoid_lowsec, avoid_nullsec):
    """Return P2 schematics with nearby planet counts and market prices, sorted by ISK/hour desc."""
    from evebs.models import MarketPrice, UniverseSystem

    nearby = find_systems_within_jumps(
        origin_system_name, max_jumps,
        avoid_lowsec=avoid_lowsec,
        avoid_nullsec=avoid_nullsec,
    )

    systems = UniverseSystem.query.filter(UniverseSystem.name.in_(nearby.keys())).all()
    system_id_to_name = {s.id: s.name for s in systems}

    p2_output_ids = [s['output']['type_id'] for s in P2_SCHEMATICS]

    prices = {
        m.type_id: m.adjusted_price
        for m in MarketPrice.query.filter(
            MarketPrice.type_id.in_(p2_output_ids),
            MarketPrice.adjusted_price.isnot(None),
        ).all()
    }

    results = []
    for sch in P2_SCHEMATICS:
        output_type_id = sch['output']['type_id']
        viable_types = set(sch['viable_planet_types'])

        sys_planet_counts = {}
        for sys_id, sys_name in system_id_to_name.items():
            count = sum(
                1 for planet in _PLANETS_BY_SYSTEM.get(str(sys_id), [])
                if planet['type_id'] in viable_types
            )
            if count:
                sys_planet_counts[sys_name] = {
                    'jumps': nearby[sys_name]['jumps'],
                    'planet_count': count,
                }

        nearby_systems = sorted(
            [{'system_name': name, **info} for name, info in sys_planet_counts.items()],
            key=lambda x: x['jumps'],
        )

        total_planets = sum(s['planet_count'] for s in nearby_systems)

        avg_price = prices.get(output_type_id, 0.0)
        cycles_per_hour = 3600.0 / sch['cycle_time']
        isk_per_hour = cycles_per_hour * sch['output']['qty'] * avg_price

        results.append({
            'output_name': sch['name'],
            'output_type_id': output_type_id,
            'cycle_time': sch['cycle_time'],
            'output_qty': sch['output']['qty'],
            'avg_price': avg_price,
            'isk_per_hour': isk_per_hour,
            'viable_planet_type_names': [
                PLANET_TYPE_NAMES.get(t, str(t)) for t in sorted(sch['viable_planet_types'])
            ],
            'nearby_planet_count': total_planets,
            'nearest_planet_jumps': nearby_systems[0]['jumps'] if nearby_systems else None,
            'nearby_systems': nearby_systems,
            'p1_names': sch['p1_names'],
        })

    results.sort(key=lambda x: x['isk_per_hour'], reverse=True)
    return results
