"""Simple factory helpers — each takes a live `db` and returns the new object."""
from datetime import datetime


def make_region(db, cpp_region_id='10000002', name='The Forge'):
    from evebs.models import Region
    r = Region(cpp_region_id=cpp_region_id, name=name)
    db.session.add(r)
    db.session.flush()
    return r


def make_universe_region(db, cpp_region_id=10000002, name='The Forge'):
    from evebs.models import UniverseRegion
    ur = UniverseRegion(cpp_region_id=cpp_region_id, name=name)
    db.session.add(ur)
    db.session.flush()
    return ur


def make_universe_constellation(db, universe_region, cpp_constellation_id=20000020, name='Kimotoro'):
    from evebs.models import UniverseConstellation
    uc = UniverseConstellation(
        cpp_constellation_id=cpp_constellation_id,
        name=name,
        universe_region_id=universe_region.id,
    )
    db.session.add(uc)
    db.session.flush()
    return uc


def make_universe_system(db, constellation=None, cpp_system_id=30000142, name='Jita'):
    from evebs.models import UniverseSystem
    us = UniverseSystem(
        cpp_system_id=cpp_system_id,
        name=name,
        security_status=0.9,
        universe_constellation_id=constellation.id if constellation else None,
    )
    db.session.add(us)
    db.session.flush()
    return us


def make_universe_station(db, system, cpp_station_id=60003760):
    from evebs.models import UniverseStation
    st = UniverseStation(
        cpp_station_id=cpp_station_id,
        name='Jita IV - Moon 4 - Caldari Navy Assembly Plant',
        office_rental_cost=0.0,
        universe_system_id=system.id,
    )
    db.session.add(st)
    db.session.flush()
    return st


def make_trade_hub(db, region, system_id=30000142, name='Jita', inner=False):
    from evebs.models import TradeHub
    th = TradeHub(eve_system_id=system_id, name=name, region_id=region.id, inner=inner)
    db.session.add(th)
    db.session.flush()
    return th


def make_station(db, trade_hub, cpp_station_id=60003760, name='Jita IV - Moon 4'):
    from evebs.models import Station
    st = Station(trade_hub_id=trade_hub.id, cpp_station_id=cpp_station_id, name=name)
    db.session.add(st)
    db.session.flush()
    return st


def make_market_group(db, cpp_market_group_id=1, name='Minerals', parent=None):
    from evebs.models import MarketGroup
    mg = MarketGroup(
        cpp_market_group_id=cpp_market_group_id,
        name=name,
        parent_id=parent.id if parent else None,
    )
    db.session.add(mg)
    db.session.flush()
    return mg


def make_item(db, cpp_eve_item_id=34, name='Tritanium', slug='tritanium',
              market_group=None, base_item=False, cost=None,
              weekly_avg_price=None, production_level=None):
    from evebs.models import EveItem
    item = EveItem(
        cpp_eve_item_id=cpp_eve_item_id,
        name=name,
        slug=slug,
        base_item=base_item,
        market_group_id=market_group.id if market_group else None,
        cost=cost,
        weekly_avg_price=weekly_avg_price,
        production_level=production_level,
    )
    db.session.add(item)
    db.session.flush()
    return item


def make_blueprint_material(db, blueprint, item, required_qtt=1):
    from evebs.models import BlueprintMaterial
    mat = BlueprintMaterial(
        blueprint_id=blueprint.id,
        eve_item_id=item.id,
        required_qtt=required_qtt,
    )
    db.session.add(mat)
    db.session.flush()
    return mat


def make_constant(db, libe, f_value, description=''):
    from evebs.models import Constant
    c = Constant(libe=libe, f_value=f_value, description=description)
    db.session.add(c)
    db.session.flush()
    return c


def make_sales_final(db, item, trade_hub, volume=100, price=1000.0,
                     day=None, order_id=9001):
    from datetime import date
    from evebs.models import SalesFinal
    sf = SalesFinal(
        day=day or date.today(),
        trade_hub_id=trade_hub.id,
        eve_item_id=item.id,
        volume=volume,
        price=price,
        order_id=order_id,
    )
    db.session.add(sf)
    db.session.flush()
    return sf


def make_blueprint(db, item, cpp_blueprint_id=None, nb_runs=1, prod_qtt=1):
    from evebs.models import Blueprint
    cpp_blueprint_id = cpp_blueprint_id or (item.cpp_eve_item_id + 100000)
    bp = Blueprint(
        cpp_blueprint_id=cpp_blueprint_id,
        produced_cpp_type_id=item.cpp_eve_item_id,
        nb_runs=nb_runs,
        prod_qtt=prod_qtt,
        name=f'{item.name} Blueprint',
    )
    db.session.add(bp)
    db.session.flush()
    item.blueprint_id = bp.id
    return bp


def make_production_list(db, user, item, trade_hub, runs_count=1):
    from evebs.models import ProductionList
    pl = ProductionList(
        user_id=user.id,
        eve_item_id=item.id,
        trade_hub_id=trade_hub.id,
        runs_count=runs_count,
    )
    db.session.add(pl)
    db.session.flush()
    return pl


def make_public_trade_order(db, item, trade_hub, order_id=1001, price=5000.0,
                             is_buy=False, volume_remain=100):
    from evebs.models import PublicTradeOrder
    o = PublicTradeOrder(
        order_id=order_id,
        trade_hub_id=trade_hub.id,
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
    from evebs.models import UserSaleOrder
    o = UserSaleOrder(
        user_id=user.id,
        eve_item_id=item.id,
        trade_hub_id=trade_hub.id,
        price=price,
    )
    db.session.add(o)
    db.session.flush()
    return o


def make_bpc_asset(db, user, item, quantity=5, station=None):
    from evebs.models import BpcAsset
    a = BpcAsset(
        user_id=user.id,
        eve_item_id=item.id,
        quantity=quantity,
        universe_station_id=station.id if station else None,
        touched=True,
    )
    db.session.add(a)
    db.session.flush()
    return a


def make_saved_list(db, user, description='My List', item_ids=None):
    import json
    from evebs.models import EveItemsSavedList
    sl = EveItemsSavedList(
        user_id=user.id,
        description=description,
        saved_ids=json.dumps(item_ids or []),
    )
    db.session.add(sl)
    db.session.flush()
    return sl
