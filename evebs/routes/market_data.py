from flask import Blueprint, render_template, abort

from evebs.extensions import db
from evebs.models import EveItem, UniverseSystem, UniverseStation, JitaMarketAnalytics, PublicTradeOrder

bp = Blueprint('market_data', __name__)


@bp.route('/market_data/<int:item_id>/market_overview/')
def market_overview(item_id):
    item = EveItem.query.get_or_404(item_id)
    jma = JitaMarketAnalytics.query.get(item_id)
    return render_template('market_data/market_overview.html',
                           item=item,
                           jma=jma,
                           title=f'Market overview for {item.name}')


@bp.route('/market_data/<int:item_id>/trade_hub_detail/<int:trade_hub_id>')
def trade_hub_detail(item_id, trade_hub_id):
    item = EveItem.query.get_or_404(item_id)
    trade_hub = db.session.get(UniverseSystem, trade_hub_id)
    if trade_hub is None:
        abort(404)
    sell_orders = (PublicTradeOrder.query
                   .filter_by(universe_system_id=trade_hub_id, eve_item_id=item.id, is_buy_order=False)
                   .order_by(PublicTradeOrder.price)
                   .limit(10)
                   .all())
    buy_orders = (PublicTradeOrder.query
                  .filter_by(universe_system_id=trade_hub_id, eve_item_id=item.id, is_buy_order=True)
                  .order_by(PublicTradeOrder.price.desc())
                  .limit(10)
                  .all())
    all_orders = sell_orders + buy_orders
    location_ids = {o.location_id for o in all_orders if o.location_id}
    station_map = {
        s.id: s.name
        for s in UniverseStation.query.filter(UniverseStation.id.in_(location_ids)).all()
    } if location_ids else {}
    return render_template('market_data/trade_hub_detail.html',
                           item=item,
                           trade_hub=trade_hub,
                           sell_orders=sell_orders,
                           buy_orders=buy_orders,
                           station_map=station_map,
                           title=f'{item.name} orders at {trade_hub.name}')
