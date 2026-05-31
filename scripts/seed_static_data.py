#!/usr/bin/env python3
"""
Seed the database from data/eve_static_data JSONL files.

Usage:
  python scripts/seed_static_data.py --all
  python scripts/seed_static_data.py --regions --market-groups
  python scripts/seed_static_data.py --regions --universe --stations --market-groups --items --blueprints
"""
import argparse
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'data', 'eve_static_data'
)

COMMIT_EVERY = 2000
PROGRESS_EVERY = 5000

# name, eve_system_id, cpp_region_id (str – matches regions.cpp_region_id), inner
TRADE_HUBS = [
    ('Jita',      30000142, '10000002', False),  # The Forge
    ('Amarr',     30002187, '10000043', False),  # Domain
    ('Dodixie',   30002659, '10000032', False),  # Sinq Laison
    ('Hek',       30002053, '10000042', False),  # Metropolis
    ('Rens',      30002510, '10000030', False),  # Heimatar
    ('Perimeter', 30000144, '10000002', True),   # The Forge (inner – near Jita)
    ('Amamake',   30002537, '10000030', False),  # Heimatar (low-sec)
]

_step_timings: list[tuple[str, float]] = []


def _jsonl(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def _en(obj, field='name'):
    val = obj.get(field)
    if isinstance(val, dict):
        return val.get('en') or next(iter(val.values()), '') or ''
    return val or ''


def _slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def _fmt(n):
    return f'{n:,}'


def _step(label):
    """Context manager-like helper — call with a label, returns a closer."""
    print(f'\n>>> {label}')
    sys.stdout.flush()
    t0 = time.perf_counter()

    def done(summary=''):
        elapsed = time.perf_counter() - t0
        msg = f'    done in {elapsed:.1f}s'
        if summary:
            msg += f'  —  {summary}'
        print(msg)
        sys.stdout.flush()
        _step_timings.append((label, elapsed))

    return done


def _progress(i, label='records'):
    print(f'    … {_fmt(i)} {label}')
    sys.stdout.flush()


# ---------------------------------------------------------------------------

def seed_regions(db, Region, UniverseRegion):
    done = _step('Regions  (mapRegions.jsonl → Region + UniverseRegion)')

    existing_r  = {r.cpp_region_id: r for r in Region.query.all()}
    existing_ur = {ur.cpp_region_id: ur for ur in UniverseRegion.query.all()}
    print(f'    existing: {_fmt(len(existing_r))} Region  |  {_fmt(len(existing_ur))} UniverseRegion')
    new_r = upd_r = new_ur = upd_ur = 0

    for obj in _jsonl('mapRegions.jsonl'):
        cpp_id = obj['_key']
        name   = _en(obj)

        r = existing_r.get(str(cpp_id))
        if r:
            r.name = name
            upd_r += 1
        else:
            r = Region(cpp_region_id=str(cpp_id), name=name)
            db.session.add(r)
            existing_r[str(cpp_id)] = r
            new_r += 1

        ur = existing_ur.get(cpp_id)
        if ur:
            ur.name = name
            upd_ur += 1
        else:
            ur = UniverseRegion(cpp_region_id=cpp_id, name=name)
            db.session.add(ur)
            existing_ur[cpp_id] = ur
            new_ur += 1

    db.session.commit()
    done(f'Region: {_fmt(new_r)} new, {_fmt(upd_r)} updated  '
         f'|  UniverseRegion: {_fmt(new_ur)} new, {_fmt(upd_ur)} updated')


def seed_market_groups(db, MarketGroup):
    done = _step('Market groups  (marketGroups.jsonl → MarketGroup)')

    existing = {mg.cpp_market_group_id: mg for mg in MarketGroup.query.all()}
    print(f'    existing: {_fmt(len(existing))} MarketGroup')
    new = updated = 0

    for obj in _jsonl('marketGroups.jsonl'):
        cpp_id     = obj['_key']
        name       = _en(obj)
        parent_cpp = obj.get('parentGroupID')

        mg = existing.get(cpp_id)
        if mg:
            mg.name = name
            mg.cpp_parent_market_group_id = parent_cpp
            updated += 1
        else:
            mg = MarketGroup(
                cpp_market_group_id=cpp_id,
                name=name,
                cpp_parent_market_group_id=parent_cpp,
                parent_id=None,
            )
            db.session.add(mg)
            existing[cpp_id] = mg
            new += 1

    db.session.commit()
    print(f'    pass 1: {_fmt(new)} new, {_fmt(updated)} updated')

    print('    pass 2: resolving parent links…')
    sys.stdout.flush()
    linked = skipped = 0
    for mg in MarketGroup.query.filter(
        MarketGroup.cpp_parent_market_group_id.isnot(None)
    ).all():
        parent = existing.get(mg.cpp_parent_market_group_id)
        if parent and mg.parent_id != parent.id:
            mg.parent_id = parent.id
            linked += 1
        elif not parent:
            skipped += 1

    db.session.commit()
    done(f'MarketGroup: {_fmt(new)} new, {_fmt(updated)} updated  '
         f'|  {_fmt(linked)} parent links set  |  {_fmt(skipped)} unresolved parents')


def seed_universe(db, UniverseConstellation, UniverseSystem, UniverseRegion):
    done_c = _step('Constellations  (mapConstellations.jsonl → UniverseConstellation)')
    region_map = {ur.cpp_region_id: ur.id for ur in UniverseRegion.query.all()}
    existing_c = {uc.cpp_constellation_id: uc for uc in UniverseConstellation.query.all()}
    print(f'    existing: {_fmt(len(existing_c))} UniverseConstellation  |  '
          f'region map size: {_fmt(len(region_map))}')
    new_c = upd_c = skip_c = 0

    for obj in _jsonl('mapConstellations.jsonl'):
        cpp_id    = obj['_key']
        name      = _en(obj)
        region_id = region_map.get(obj.get('regionID'))
        if not region_id:
            skip_c += 1
            continue

        uc = existing_c.get(cpp_id)
        if uc:
            uc.name = name
            uc.universe_region_id = region_id
            upd_c += 1
        else:
            uc = UniverseConstellation(
                cpp_constellation_id=cpp_id,
                name=name,
                universe_region_id=region_id,
            )
            db.session.add(uc)
            existing_c[cpp_id] = uc
            new_c += 1

    db.session.commit()
    done_c(f'UniverseConstellation: {_fmt(new_c)} new, {_fmt(upd_c)} updated, '
           f'{_fmt(skip_c)} skipped (no region)')

    done_s = _step('Solar systems  (mapSolarSystems.jsonl → UniverseSystem)')
    const_map  = {uc.cpp_constellation_id: uc.id for uc in UniverseConstellation.query.all()}
    existing_s = {us.cpp_system_id: us for us in UniverseSystem.query.all()}
    print(f'    existing: {_fmt(len(existing_s))} UniverseSystem  |  '
          f'constellation map size: {_fmt(len(const_map))}')
    new_s = upd_s = skip_s = 0
    i = 0

    for obj in _jsonl('mapSolarSystems.jsonl'):
        cpp_id   = obj['_key']
        name     = _en(obj)
        const_id = const_map.get(obj.get('constellationID'))
        if not const_id:
            skip_s += 1
            continue

        us = existing_s.get(cpp_id)
        if us:
            us.name = name
            us.security_status = obj.get('securityStatus', 0.0)
            us.security_class  = obj.get('securityClass')
            us.cpp_star_id     = obj.get('starID')
            us.universe_constellation_id = const_id
            upd_s += 1
        else:
            us = UniverseSystem(
                cpp_system_id=cpp_id,
                name=name,
                security_status=obj.get('securityStatus', 0.0),
                security_class=obj.get('securityClass'),
                cpp_star_id=obj.get('starID'),
                universe_constellation_id=const_id,
            )
            db.session.add(us)
            existing_s[cpp_id] = us
            new_s += 1

        i += 1
        if i % COMMIT_EVERY == 0:
            db.session.flush()
        if i % PROGRESS_EVERY == 0:
            _progress(i, 'solar systems')

    db.session.commit()
    done_s(f'UniverseSystem: {_fmt(new_s)} new, {_fmt(upd_s)} updated, '
           f'{_fmt(skip_s)} skipped  |  {_fmt(i)} total processed')


def seed_stations(db, UniverseStation, UniverseSystem):
    done = _step('NPC stations  (npcStations.jsonl → UniverseStation)')
    system_map = {us.cpp_system_id: us.id for us in UniverseSystem.query.all()}
    existing   = {st.id: st for st in UniverseStation.query.all()}
    print(f'    existing: {_fmt(len(existing))} UniverseStation  |  '
          f'system map size: {_fmt(len(system_map))}')
    new = updated = skipped = 0

    for obj in _jsonl('npcStations.jsonl'):
        cpp_id    = obj['_key']
        system_id = system_map.get(obj.get('solarSystemID'))
        if not system_id:
            skipped += 1
            continue

        st = existing.get(cpp_id)
        if st:
            st.universe_system_id = system_id
            updated += 1
        else:
            st = UniverseStation(
                id=cpp_id,
                name='',
                office_rental_cost=0.0,
                universe_system_id=system_id,
            )
            db.session.add(st)
            existing[cpp_id] = st
            new += 1

    db.session.commit()
    done(f'UniverseStation: {_fmt(new)} new, {_fmt(updated)} updated, '
         f'{_fmt(skipped)} skipped (no system)')


def seed_items(db, EveItem, MarketGroup):
    done = _step('Eve items  (types.jsonl → EveItem)')
    mg_map   = {mg.cpp_market_group_id: mg.id for mg in MarketGroup.query.all()}
    existing = {ei.cpp_eve_item_id: ei for ei in EveItem.query.all()}
    used_slugs = {ei.slug for ei in existing.values() if ei.slug}
    print(f'    existing: {_fmt(len(existing))} EveItem  |  '
          f'market group map size: {_fmt(len(mg_map))}')
    new = updated = skipped_unpublished = skipped_noname = 0
    slug_collisions = 0
    i = 0

    for obj in _jsonl('types.jsonl'):
        if not obj.get('published', False):
            skipped_unpublished += 1
            continue

        cpp_id = obj['_key']
        name   = _en(obj)
        if not name:
            skipped_noname += 1
            continue

        desc      = _en(obj, 'description') or None
        mg_cpp_id = obj.get('marketGroupID')
        mg_id     = mg_map.get(mg_cpp_id) if mg_cpp_id else None

        item = existing.get(cpp_id)
        if item:
            item.name            = name
            item.volume          = obj.get('volume')
            item.mass            = obj.get('mass')
            item.description     = desc
            item.market_group_id = mg_id
            updated += 1
        else:
            slug = _slugify(name)
            if slug in used_slugs:
                slug = f'{slug}-{cpp_id}'
                slug_collisions += 1
            used_slugs.add(slug)

            item = EveItem(
                cpp_eve_item_id=cpp_id,
                name=name,
                slug=slug,
                volume=obj.get('volume'),
                mass=obj.get('mass'),
                description=desc,
                market_group_id=mg_id,
            )
            db.session.add(item)
            existing[cpp_id] = item
            new += 1

        i += 1
        if i % COMMIT_EVERY == 0:
            db.session.flush()
        if i % PROGRESS_EVERY == 0:
            _progress(i, 'types')

    db.session.commit()
    done(f'EveItem: {_fmt(new)} new, {_fmt(updated)} updated  '
         f'|  {_fmt(i)} published processed  '
         f'|  skipped: {_fmt(skipped_unpublished)} unpublished, {_fmt(skipped_noname)} no-name  '
         f'|  {_fmt(slug_collisions)} slug collisions resolved')


def seed_blueprints(db, Blueprint, BlueprintMaterial, EveItem):
    done = _step('Blueprints  (blueprints.jsonl → Blueprint + BlueprintMaterial)')
    item_map    = {ei.cpp_eve_item_id: ei for ei in EveItem.query.all()}
    existing_bp = {bp.cpp_blueprint_id: bp for bp in Blueprint.query.all()}
    existing_bp_by_product = {bp.produced_cpp_type_id: bp for bp in existing_bp.values()}
    print(f'    existing: {_fmt(len(existing_bp))} Blueprint  |  '
          f'item map size: {_fmt(len(item_map))}')
    bp_new = bp_updated = mat_total = skipped_no_mfg = skipped_no_product = 0
    unknown_products = 0
    i = 0

    for obj in _jsonl('blueprints.jsonl'):
        mfg = obj.get('activities', {}).get('manufacturing')
        if not mfg:
            skipped_no_mfg += 1
            continue

        products = mfg.get('products', [])
        if not products:
            skipped_no_product += 1
            continue

        product           = products[0]
        produced_cpp_id   = product['typeID']
        prod_qtt          = product.get('quantity', 1)
        nb_runs           = obj.get('maxProductionLimit', 1)
        cpp_bp_id         = obj['_key']
        produced_item     = item_map.get(produced_cpp_id)
        if not produced_item:
            unknown_products += 1
        bp_name = produced_item.name if produced_item else f'Unknown ({produced_cpp_id})'

        bp = existing_bp.get(cpp_bp_id) or existing_bp_by_product.get(produced_cpp_id)
        if bp:
            bp.nb_runs              = nb_runs
            bp.prod_qtt             = prod_qtt
            bp.name                 = bp_name
            bp.produced_cpp_type_id = produced_cpp_id
            BlueprintMaterial.query.filter_by(blueprint_id=bp.id).delete()
            bp_updated += 1
        else:
            bp = Blueprint(
                cpp_blueprint_id=cpp_bp_id,
                produced_cpp_type_id=produced_cpp_id,
                nb_runs=nb_runs,
                prod_qtt=prod_qtt,
                name=bp_name,
            )
            db.session.add(bp)
            db.session.flush()
            existing_bp[cpp_bp_id] = bp
            existing_bp_by_product[produced_cpp_id] = bp
            bp_new += 1

        if produced_item:
            produced_item.blueprint_id = bp.id

        mat_count = 0
        for mat in mfg.get('materials', []):
            mat_item = item_map.get(mat['typeID'])
            if not mat_item:
                continue
            db.session.add(BlueprintMaterial(
                blueprint_id=bp.id,
                required_qtt=mat['quantity'],
                eve_item_id=mat_item.id,
            ))
            mat_count += 1
            mat_total += 1

        i += 1
        if i % COMMIT_EVERY == 0:
            db.session.flush()
        if i % PROGRESS_EVERY == 0:
            _progress(i, 'blueprints')

    db.session.commit()
    done(f'Blueprint: {_fmt(bp_new)} new, {_fmt(bp_updated)} updated  '
         f'|  BlueprintMaterial: {_fmt(mat_total)} written  '
         f'|  skipped: {_fmt(skipped_no_mfg)} no-mfg, {_fmt(skipped_no_product)} no-product  '
         f'|  {_fmt(unknown_products)} unknown product items')


def seed_trade_hubs(db, UniverseSystem):
    done = _step('Trade hubs  (hardcoded list → UniverseSystem.trade_hub)')
    existing = {us.cpp_system_id: us for us in UniverseSystem.query.all()}
    print(f'    existing: {_fmt(len(existing))} UniverseSystem rows  |  seeding {len(TRADE_HUBS)} trade hubs')
    updated = skipped = 0

    for name, system_id, cpp_region_id, inner in TRADE_HUBS:
        us = existing.get(system_id)
        if us is None:
            print(f'    WARNING: UniverseSystem cpp_system_id={system_id} ({name}) not found — run --universe first')
            skipped += 1
            continue
        us.trade_hub = True
        us.is_inner = inner
        updated += 1

    db.session.commit()
    done(f'UniverseSystem trade_hub: {_fmt(updated)} updated, {_fmt(skipped)} skipped')


# ---------------------------------------------------------------------------

def _print_summary(wall: float):
    if not _step_timings:
        return
    print('\n' + '=' * 60)
    print('  SUMMARY')
    print('=' * 60)
    for label, elapsed in _step_timings:
        bar = '█' * max(1, int(elapsed / max(t for _, t in _step_timings) * 30))
        print(f'  {elapsed:6.1f}s  {bar}  {label}')
    print('-' * 60)
    print(f'  total wall time: {wall:.1f}s')
    print('=' * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Seed the database from data/eve_static_data JSONL files.'
    )
    parser.add_argument('--all',           action='store_true', help='Seed everything in dependency order')
    parser.add_argument('--regions',       action='store_true', help='Seed Region + UniverseRegion')
    parser.add_argument('--market-groups', action='store_true', help='Seed MarketGroup')
    parser.add_argument('--universe',      action='store_true', help='Seed UniverseConstellation + UniverseSystem (requires --regions first)')
    parser.add_argument('--stations',      action='store_true', help='Seed UniverseStation (requires --universe first)')
    parser.add_argument('--items',         action='store_true', help='Seed EveItem (requires --market-groups first)')
    parser.add_argument('--blueprints',    action='store_true', help='Seed Blueprint + BlueprintMaterial (requires --items first)')
    parser.add_argument('--trade-hubs',    action='store_true', help='Seed TradeHub (requires --regions first)')
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(1)

    from evebs import create_app
    from evebs.extensions import db
    from evebs.models import (
        Region, UniverseRegion, MarketGroup,
        UniverseConstellation, UniverseSystem,
        UniverseStation, EveItem, Blueprint, BlueprintMaterial,
    )

    app = create_app()
    wall_t0 = time.perf_counter()

    with app.app_context():
        do_regions       = args.all or args.regions
        do_market_groups = args.all or args.market_groups
        do_universe      = args.all or args.universe
        do_stations      = args.all or args.stations
        do_items         = args.all or args.items
        do_blueprints    = args.all or args.blueprints
        do_trade_hubs    = args.all or args.trade_hubs

        if do_regions:
            seed_regions(db, Region, UniverseRegion)
        if do_market_groups:
            seed_market_groups(db, MarketGroup)
        if do_universe:
            seed_universe(db, UniverseConstellation, UniverseSystem, UniverseRegion)
        if do_stations:
            seed_stations(db, UniverseStation, UniverseSystem)
        if do_items:
            seed_items(db, EveItem, MarketGroup)
        if do_blueprints:
            seed_blueprints(db, Blueprint, BlueprintMaterial, EveItem)
        if do_trade_hubs:
            seed_trade_hubs(db, UniverseSystem)

    _print_summary(time.perf_counter() - wall_t0)


if __name__ == '__main__':
    main()
