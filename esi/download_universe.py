"""Download the full Eve universe hierarchy: regions → constellations → systems → stations."""
from esi.client import EsiClient
from evebs.extensions import db
from evebs.models import UniverseRegion, UniverseConstellation, UniverseSystem, UniverseStation


def download_universe():
    client = EsiClient('universe/regions/')
    region_ids = client.get_all_pages()
    print(f'Found {len(region_ids)} regions')

    for i, region_id in enumerate(region_ids, 1):
        detail = EsiClient(f'universe/regions/{region_id}/').get_page()
        if not detail:
            print(f'[{i}/{len(region_ids)}] Region {region_id}: no data, skipping')
            continue

        name = detail.get('name', '')
        constellation_ids = detail.get('constellations', [])

        region = UniverseRegion.query.filter_by(cpp_region_id=region_id).first()
        if not region:
            region = UniverseRegion(
                cpp_region_id=region_id,
                name=name,
                description=detail.get('description'),
                constellations=constellation_ids,
            )
            db.session.add(region)
            print(f'[{i}/{len(region_ids)}] + Region: {name} ({len(constellation_ids)} constellations)')
        else:
            region.name = name
            region.description = detail.get('description', region.description)
            region.constellations = constellation_ids
            print(f'[{i}/{len(region_ids)}] ~ Region: {name} ({len(constellation_ids)} constellations)')

        db.session.flush()
        _download_constellations(region, constellation_ids)
        db.session.commit()

    print('Universe download complete.')


def _download_constellations(region, constellation_ids):
    for constellation_id in constellation_ids:
        detail = EsiClient(f'universe/constellations/{constellation_id}/').get_page()
        if not detail:
            print(f'  Constellation {constellation_id}: no data, skipping')
            continue

        name = detail.get('name', '')
        system_ids = detail.get('systems', [])

        constellation = UniverseConstellation.query.filter_by(
            cpp_constellation_id=constellation_id
        ).first()
        if not constellation:
            constellation = UniverseConstellation(
                cpp_constellation_id=constellation_id,
                name=name,
                universe_region_id=region.id,
            )
            db.session.add(constellation)
            print(f'  + Constellation: {name} ({len(system_ids)} systems)')
        else:
            constellation.name = name
            print(f'  ~ Constellation: {name} ({len(system_ids)} systems)')

        db.session.flush()
        _download_systems(constellation, system_ids)


def _download_systems(constellation, system_ids):
    for system_id in system_ids:
        detail = EsiClient(f'universe/systems/{system_id}/').get_page()
        if not detail:
            print(f'    System {system_id}: no data, skipping')
            continue

        name = detail.get('name', '')
        sec = detail.get('security_status', 0.0)
        station_ids = detail.get('stations', [])

        system = UniverseSystem.query.filter_by(cpp_system_id=system_id).first()
        if not system:
            system = UniverseSystem(
                cpp_system_id=system_id,
                name=name,
                security_status=sec,
                security_class=detail.get('security_class'),
                cpp_star_id=detail.get('star_id'),
                universe_constellation_id=constellation.id,
            )
            db.session.add(system)
            verb = '+'
        else:
            system.name = name
            system.security_status = sec
            system.security_class = detail.get('security_class', system.security_class)
            system.cpp_star_id = detail.get('star_id', system.cpp_star_id)
            verb = '~'

        print(f'    {verb} System: {name} (sec {sec:.2f}, {len(station_ids)} stations)')

        db.session.flush()
        _download_stations(system, station_ids)


def _download_stations(system, station_ids):
    for station_id in station_ids:
        detail = EsiClient(f'universe/stations/{station_id}/').get_page()
        if not detail:
            print(f'      Station {station_id}: no data, skipping')
            continue

        name = detail.get('name', '')

        station = UniverseStation.query.filter_by(cpp_station_id=station_id).first()
        if not station:
            station = UniverseStation(
                cpp_station_id=station_id,
                name=name,
                office_rental_cost=detail.get('office_rental_cost', 0.0),
                security_status=detail.get('security_status'),
                universe_system_id=system.id,
            )
            db.session.add(station)
            verb = '+'
        else:
            station.name = name
            station.office_rental_cost = detail.get('office_rental_cost', station.office_rental_cost)
            station.security_status = detail.get('security_status', station.security_status)
            verb = '~'

        station.services = detail.get('services', [])
        print(f'      {verb} Station: {name}')


if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from run import app
    with app.app_context():
        download_universe()
