"""Download market orders per region, cascading-creating types/groups/categories as needed."""
from datetime import datetime

from esi.client import EsiClient
from esi.errors import NotFound
from evebs.extensions import db
from evebs.models import (
    UniverseRegion, UniverseSystem,
    UniverseCategory, UniverseGroup, UniverseType,
    MarketGroup, MarketOrder, IndustryInterestingItem,
)


def download_region_orders(interesting_only=False):
    """Fetch and upsert market orders for every region, creating missing types on the fly.

    If interesting_only is True, only download orders for items listed in
    IndustryInterestingItem for each region.
    """
    regions = UniverseRegion.query.all()
    known_system_ids = {r[0] for r in UniverseSystem.query.with_entities(UniverseSystem.id).all()}

    for i, region in enumerate(regions, 1):
        if interesting_only:
            allowed = {r.item_id for r in IndustryInterestingItem.query.filter_by(region_id=region.id).all()}
            if not allowed:
                continue
        try:
            type_ids = EsiClient(f'markets/{region.id}/types/').get_all_pages()
        except NotFound:
            print(f'[{i}/{len(regions)}] {region.name}: no types, skipping')
            continue

        if interesting_only:
            type_ids = [t for t in type_ids if t in allowed]
            if not type_ids:
                continue

        print(f'[{i}/{len(regions)}] {region.name} ({len(type_ids)} types)')

        for j, type_id in enumerate(type_ids, 1):
            _ensure_type(type_id)
            try:
                orders = EsiClient(
                    f'markets/{region.id}/orders/',
                    params={'order_type': 'all', 'type_id': type_id},
                ).get_all_pages()
            except NotFound:
                continue

            inserted = updated = 0
            for order in orders:
                if order['system_id'] not in known_system_ids:
                    continue
                if _upsert_order(order):
                    inserted += 1
                else:
                    updated += 1

            print(f'  [{j}/{len(type_ids)}] type {type_id}: {len(orders)} orders (+{inserted} ~{updated})')
            db.session.commit()

    print('Region orders download complete.')


def _upsert_order(order):
    """Insert or update a MarketOrder. Returns True if inserted, False if updated."""
    issued = datetime.strptime(order['issued'], '%Y-%m-%dT%H:%M:%SZ')
    existing = MarketOrder.query.filter_by(id=order['order_id']).first()
    if existing:
        existing.price = order['price']
        existing.volume_remain = order['volume_remain']
        existing.issued = issued
        return False
    else:
        db.session.add(MarketOrder(
            id=order['order_id'],
            duration=order['duration'],
            is_buy_order=order['is_buy_order'],
            issued=issued,
            location_id=order['location_id'],
            min_volume=order['min_volume'],
            price=order['price'],
            range=order['range'],
            system_id=order['system_id'],
            type_id=order['type_id'],
            volume_remain=order['volume_remain'],
            volume_total=order['volume_total'],
            source='list_order_in_a_region',
        ))
        return True


def _ensure_type(type_id):
    """Fetch and upsert a universe type, creating its group/category/market-group as needed."""
    detail = EsiClient(f'universe/types/{type_id}/').get_page()
    if not detail:
        return

    _ensure_group(detail['group_id'])

    market_group_id = detail.get('market_group_id')
    if market_group_id:
        _ensure_market_group(market_group_id)

    existing = UniverseType.query.filter_by(id=type_id).first()
    if existing:
        existing.name = detail['name']
        existing.description = detail['description']
        existing.published = detail['published']
        print(f'  ~ Type: {detail["name"]}')
    else:
        db.session.add(UniverseType(
            id=type_id,
            name=detail['name'],
            description=detail['description'],
            group_id=detail['group_id'],
            market_group_id=market_group_id,
            published=detail['published'],
            capacity=detail['capacity'],
            graphic_id=detail.get('graphic_id'),
            icon_id=detail.get('icon_id'),
            mass=detail['mass'],
            packaged_volume=detail['packaged_volume'],
            portion_size=detail['portion_size'],
            radius=detail['radius'],
            volume=detail['volume'],
        ))
        print(f'  + Type: {detail["name"]}')

    db.session.flush()


def _ensure_group(group_id):
    """Fetch and upsert a universe group if it doesn't already exist."""
    if UniverseGroup.query.filter_by(id=group_id).first():
        return

    detail = EsiClient(f'universe/groups/{group_id}/').get_page()
    if not detail:
        return

    _ensure_category(detail['category_id'])

    db.session.add(UniverseGroup(
        id=group_id,
        name=detail['name'],
        published=detail['published'],
        category_id=detail['category_id'],
    ))
    print(f'    + Group: {detail["name"]}')
    db.session.flush()


def _ensure_category(category_id):
    """Fetch and upsert a universe category if it doesn't already exist."""
    if UniverseCategory.query.filter_by(id=category_id).first():
        return

    detail = EsiClient(f'universe/categories/{category_id}/').get_page()
    if not detail:
        return

    db.session.add(UniverseCategory(
        id=category_id,
        name=detail['name'],
        published=detail['published'],
    ))
    print(f'      + Category: {detail["name"]}')
    db.session.flush()


def _ensure_market_group(market_group_id):
    """Fetch and upsert a market group tree node, recursing to create parent first."""
    if MarketGroup.query.filter_by(id=market_group_id).first():
        return

    detail = EsiClient(f'markets/groups/{market_group_id}/').get_page()
    if not detail:
        return

    parent_group_id = detail.get('parent_group_id')
    if parent_group_id:
        _ensure_market_group(parent_group_id)

    db.session.add(MarketGroup(
        id=market_group_id,
        name=detail['name'],
        description=detail['description'],
        parent_group_id=parent_group_id,
    ))
    print(f'    + MarketGroup: {detail["name"]}')
    db.session.flush()


if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from run import app
    with app.app_context():
        download_region_orders(interesting_only='--interesting-only' in sys.argv or '-i' in sys.argv)
