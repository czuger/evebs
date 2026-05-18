from flask import Blueprint, render_template, abort
from flask_login import current_user

from evebs.models import UniverseType, TradeHub, PricesMin, PriceAdvicesMinPrice, PublicTradeOrder

bp = Blueprint('market_data', __name__)


@bp.route('/market_data/<int:item_id>/market_overview/')
def market_overview(item_id):
    """Render price comparison across trade hubs for an item."""
    item = UniverseType.query.get_or_404(item_id)
    if item.base_item:
        item_prices = (PricesMin.query
                       .filter_by(eve_item_id=item.id)
                       .join(PricesMin.trade_hub)
                       .order_by(PricesMin.min_price)
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
    """Render current sell orders for an item at a specific hub."""
    item = UniverseType.query.get_or_404(item_id)
    trade_hub = TradeHub.query.get_or_404(trade_hub_id)
    orders = (PublicTradeOrder.query
              .filter_by(trade_hub_id=trade_hub_id, eve_item_id=item.id, is_buy_order=False)
              .order_by(PublicTradeOrder.price)
              .limit(20)
              .all())
    return render_template('market_data/trade_hub_detail.html',
                           element=item,
                           trade_hub=trade_hub,
                           orders=orders,
                           title=f'{item.name} current sell orders at {trade_hub.name}')
