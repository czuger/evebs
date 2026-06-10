"""Simple factory helpers — each takes a live `db` and returns the new object."""
import json
from datetime import date, datetime

from evebs.models import (
    Blueprint,
    EveItem,
    EveItemsSavedList,
    IndustryJob,
    JitaMarketAnalytics,
    MarketGroup,
    ProductionList,
    PublicTradeOrder,
    SalesFinal,
    UniverseConstellation,
    UniverseRegion,
    UniverseStation,
    UniverseStructure,
    UniverseSystem,
    UserAsset,
    UserSaleOrder,
)


def make_universe_region(db, region_id=10000002, name='The Forge'):
    ur = UniverseRegion(id=region_id, name=name)
    db.session.add(ur)
    db.session.flush()
    return ur


def make_universe_constellation(db, universe_region, constellation_id=20000020, name='Kimotoro'):
    uc = UniverseConstellation(
        id=constellation_id,
        name=name,
        universe_region_id=universe_region.id,
    )
    db.session.add(uc)
    db.session.flush()
    return uc


def make_universe_system(db, constellation=None, system_id=30000142, name='Jita'):
    us = UniverseSystem(
        id=system_id,
        name=name,
        security_status=0.9,
        universe_constellation_id=constellation.id if constellation else None,
    )
    db.session.add(us)
    db.session.flush()
    return us


def make_universe_station(db, system, station_id=60003760):
    st = UniverseStation(
        id=station_id,
        name='Jita IV - Moon 4 - Caldari Navy Assembly Plant',
        office_rental_cost=0.0,
        universe_system_id=system.id,
    )
    db.session.add(st)
    db.session.flush()
    return st


def make_trade_hub(db, system, inner=False):
    system.trade_hub = True
    system.is_inner = inner
    db.session.flush()
    return system


def make_market_group(db, group_id=1, name='Minerals', parent=None):
    mg = MarketGroup(
        id=group_id,
        name=name,
        parent_id=parent.id if parent else None,
    )
    db.session.add(mg)
    db.session.flush()
    return mg


def make_item(db, item_id=34, name='Tritanium', slug='tritanium',
              market_group=None, base_item=False, production_level=None):
    item = EveItem(
        id=item_id,
        name=name,
        slug=slug,
        base_item=base_item,
        market_group_id=market_group.id if market_group else None,
        production_level=production_level,
    )
    db.session.add(item)
    db.session.flush()
    return item


def make_sales_final(db, item, trade_hub, volume=100, price=1000.0,
                     day=None, order_id=9001):
    sf = SalesFinal(
        day=day or date.today(),
        universe_system_id=trade_hub.id,
        eve_item_id=item.id,
        volume=volume,
        price=price,
        order_id=order_id,
    )
    db.session.add(sf)
    db.session.flush()
    return sf


def make_blueprint(db, item, blueprint_id=None, nb_runs=1, prod_qtt=1, manufacturing_cost=None):
    blueprint_id = blueprint_id or (item.id + 100000)
    bp = Blueprint(
        id=blueprint_id,
        produced_type_id=item.id,
        nb_runs=nb_runs,
        prod_qtt=prod_qtt,
        name=f'{item.name} Blueprint',
        manufacturing_cost=manufacturing_cost,
    )
    db.session.add(bp)
    db.session.flush()
    item.blueprint_id = bp.id
    return bp


def make_production_list(db, user, item, trade_hub, runs_count=1):
    pl = ProductionList(
        user_id=user.id,
        eve_item_id=item.id,
        universe_system_id=trade_hub.id,
        runs_count=runs_count,
    )
    db.session.add(pl)
    db.session.flush()
    return pl


def make_public_trade_order(db, item, trade_hub, order_id=1001, price=5000.0,
                             is_buy=False, volume_remain=100):
    o = PublicTradeOrder(
        order_id=order_id,
        universe_system_id=trade_hub.id,
        eve_item_id=item.id,
        is_buy_order=is_buy,
        end_time=datetime(2026, 12, 31),
        price=price,
        range='station',
        volume_remain=volume_remain,
        volume_total=1000,
        min_volume=1,
    )
    db.session.add(o)
    db.session.flush()
    return o


def make_user_sale_order(db, user, item, trade_hub, price=10000.0):
    o = UserSaleOrder(
        user_id=user.id,
        eve_item_id=item.id,
        universe_system_id=trade_hub.id,
        price=price,
    )
    db.session.add(o)
    db.session.flush()
    return o


def make_universe_structure(db, system, structure_id=1_000_000_000_001,
                            name='Test Structure', owner_id=1, type_id=35835):
    s = UniverseStructure(
        id=structure_id,
        name=name,
        owner_id=owner_id,
        type_id=type_id,
        universe_system_id=system.id,
    )
    db.session.add(s)
    db.session.flush()
    return s


def make_user_asset(db, user, item, quantity=5, station=None, esi_item_id=None,
                   structure_id=None, is_blueprint_copy=False):
    a = UserAsset(
        user_id=user.id,
        eve_item_id=item.id,
        quantity=quantity,
        universe_station_id=station.id if station else None,
        universe_structure_id=structure_id,
        esi_item_id=esi_item_id,
        is_blueprint_copy=is_blueprint_copy,
        touched=True,
    )
    db.session.add(a)
    db.session.flush()
    return a


def make_jma(db, item, min_sell_price=1000.0):
    jma = JitaMarketAnalytics(id=item.id, min_sell_price=min_sell_price)
    db.session.add(jma)
    db.session.flush()
    return jma


def make_saved_list(db, user, description='My List', item_ids=None):
    sl = EveItemsSavedList(
        user_id=user.id,
        description=description,
        saved_ids=json.dumps(item_ids or []),
    )
    db.session.add(sl)
    db.session.flush()
    return sl
