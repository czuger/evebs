"""Industry facility search utilities."""
from sqlalchemy.orm import joinedload
from evebs.engine.routing import find_systems_within_jumps
from evebs.models import IndustryFacility, UniverseSystem


def get_industry_facilities_near(origin, max_jumps=5, activity='manufacturing',
                                  avoid_lowsec=False, avoid_nullsec=False):
    """Return industry facilities within max_jumps of origin, sorted by total cost.

    Returns a list of dicts with keys: facility_id, name, system_name, region_name,
    jumps, security, cost_index, tax, total_cost; sorted ascending by total_cost.
    """
    nearby_info = find_systems_within_jumps(
        origin, max_jumps,
        avoid_lowsec=avoid_lowsec,
        avoid_nullsec=avoid_nullsec,
    )

    from evebs.models import UniverseConstellation
    systems = (UniverseSystem.query
               .options(joinedload(UniverseSystem.universe_constellation)
                        .joinedload(UniverseConstellation.universe_region))
               .filter(UniverseSystem.name.in_(nearby_info.keys()))
               .all())
    system_by_id = {s.id: s for s in systems}

    facilities = IndustryFacility.query.filter(
        IndustryFacility.universe_system_id.in_(system_by_id.keys())
    ).all()

    results = []
    for f in facilities:
        sys_obj = system_by_id.get(f.universe_system_id)
        if not sys_obj:
            continue
        sys_info = nearby_info.get(sys_obj.name, {})
        cost_index = 0.0
        if sys_obj.cost_indices:
            for entry in sys_obj.cost_indices:
                if entry.get('activity') == activity:
                    cost_index = entry.get('cost_index', 0.0)
                    break
        tax = f.tax or 0.0
        name = (f.universe_station.name if f.universe_station
                else f'Structure #{f.id}')
        constellation = sys_obj.universe_constellation
        region_name = constellation.universe_region.name if constellation and constellation.universe_region else ''
        results.append({
            'facility_id': f.id,
            'name': name,
            'system_name': sys_obj.name,
            'region_name': region_name,
            'jumps': sys_info.get('jumps', 0),
            'security': round(sys_obj.security_status, 2),
            'cost_index': cost_index,
            'tax': tax,
            'total_cost': cost_index + tax,
        })

    results.sort(key=lambda x: x['total_cost'])
    return results
