from flask import Blueprint as FlaskBlueprint, render_template, abort

from evebs.extensions import db
from evebs.models import EveItem, UniverseSystem, UniverseStation, PublicTradeOrder

bp = FlaskBlueprint('market_data', __name__)


def _item_market(item_id, system_id=None):
    """Top 10 sell + top 10 buy public orders for an item, optionally restricted to one
    system. Returns (item, sell_orders, buy_orders, station_map, system_map)."""
    item = EveItem.query.get_or_404(item_id)
    q = PublicTradeOrder.query.filter_by(eve_item_id=item.id)
    if system_id is not None:
        q = q.filter_by(universe_system_id=system_id)
    sell_orders = q.filter_by(is_buy_order=False).order_by(PublicTradeOrder.price).limit(10).all()
    buy_orders  = q.filter_by(is_buy_order=True).order_by(PublicTradeOrder.price.desc()).limit(10).all()

    orders = sell_orders + buy_orders
    loc_ids = {o.location_id for o in orders if o.location_id}
    station_map = {
        s.id: s.name
        for s in UniverseStation.query.filter(UniverseStation.id.in_(loc_ids)).all()
    } if loc_ids else {}

    sys_ids = {o.universe_system_id for o in orders}
    system_map = {}
    for s in (UniverseSystem.query.filter(UniverseSystem.id.in_(sys_ids)).all() if sys_ids else []):
        region = (s.universe_constellation.universe_region.name
                  if s.universe_constellation and s.universe_constellation.universe_region else '')
        system_map[s.id] = f'{s.name} ({region})' if region else s.name

    return item, sell_orders, buy_orders, station_map, system_map


@bp.route('/market_data/<int:item_id>/market_overview/')
def market_overview(item_id):
    item, sell_orders, buy_orders, station_map, system_map = _item_market(item_id)
    return render_template('market_data/market_overview.html',
                           item=item,
                           sell_orders=sell_orders,
                           buy_orders=buy_orders,
                           station_map=station_map,
                           system_map=system_map,
                           show_system=True,
                           title=f'Market overview for {item.name}')


@bp.route('/market_data/<int:item_id>/trade_hub_detail/<int:trade_hub_id>')
def trade_hub_detail(item_id, trade_hub_id):
    item, sell_orders, buy_orders, station_map, system_map = _item_market(item_id, system_id=trade_hub_id)
    trade_hub = db.session.get(UniverseSystem, trade_hub_id)
    if trade_hub is None:
        abort(404)
    return render_template('market_data/trade_hub_detail.html',
                           item=item,
                           trade_hub=trade_hub,
                           sell_orders=sell_orders,
                           buy_orders=buy_orders,
                           station_map=station_map,
                           system_map=system_map,
                           show_system=False,
                           title=f'{item.name} orders at {trade_hub.name}')
