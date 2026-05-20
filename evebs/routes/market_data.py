from flask import Blueprint, render_template, abort
from flask_login import current_user

from evebs.models import UniverseType, UniverseSystem, MarketSellerPrice, MarketBuyerPrice, PriceAdvicesMinPrice, MarketOrder, UniverseStation

bp = Blueprint('market_data', __name__)


@bp.route('/market_data/<int:item_id>/market_overview/')
def market_overview(item_id):
    """Render price comparison across trade hubs for an item."""
    item = UniverseType.query.get_or_404(item_id)
    if item.blueprint is None:
        item_prices = (MarketSellerPrice.query
                       .filter_by(type_id=item.id)
                       .join(MarketSellerPrice.universe_system)
                       .filter(UniverseSystem.trade_hub == True)  # noqa: E712
                       .order_by(MarketSellerPrice.p10_price)
                       .all())
        advice_prices = None
    else:
        item_prices = None
        advice_prices = (PriceAdvicesMinPrice.query
                         .filter_by(eve_item_id=item.id)
                         .filter(PriceAdvicesMinPrice.margin_percent.isnot(None))
                         .order_by(PriceAdvicesMinPrice.vol_month.desc(),
                                   PriceAdvicesMinPrice.margin_percent.desc())
                         .all())
    return render_template('market_data/market_overview.html',
                           item=item,
                           item_prices=item_prices,
                           advice_prices=advice_prices,
                           title=f'Trade hubs prices comparison for {item.name}')


@bp.route('/market_data/<int:item_id>/trade_hub_detail/<int:trade_hub_id>')
def trade_hub_detail(item_id, trade_hub_id):
    """Render current sell and buy orders for an item at a specific hub."""
    item = UniverseType.query.get_or_404(item_id)
    trade_hub = UniverseSystem.query.get_or_404(trade_hub_id)
    sell_orders = (MarketOrder.query
                   .filter_by(system_id=trade_hub.id, type_id=item.id, is_buy_order=False)
                   .order_by(MarketOrder.price)
                   .limit(20)
                   .all())
    buy_orders = (MarketOrder.query
                  .filter_by(system_id=trade_hub.id, type_id=item.id, is_buy_order=True)
                  .order_by(MarketOrder.price.desc())
                  .limit(20)
                  .all())
    seller_price = MarketSellerPrice.query.filter_by(type_id=item.id, system_id=trade_hub.id).first()
    buyer_price = MarketBuyerPrice.query.filter_by(type_id=item.id, system_id=trade_hub.id).first()
    all_location_ids = {o.location_id for o in sell_orders + buy_orders}
    stations = UniverseStation.query.filter(UniverseStation.id.in_(all_location_ids)).all()
    station_names = {s.id: s.name for s in stations}
    return render_template('market_data/trade_hub_detail.html',
                           element=item,
                           trade_hub=trade_hub,
                           sell_orders=sell_orders,
                           buy_orders=buy_orders,
                           seller_price=seller_price,
                           buyer_price=buyer_price,
                           station_names=station_names,
                           title=f'{item.name} at {trade_hub.name}')
