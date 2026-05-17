from flask import Blueprint, render_template, abort
from flask_login import current_user

from evebs.models import TradeHub, Constant, UniverseType, MarketPrice

bp = Blueprint('items', __name__)


@bp.route('/items/<id>')
def show(id):
    item = UniverseType.query.get(id)
    if item is None:
        abort(404)
    jita = TradeHub.query.filter_by(eve_system_id=30000142).first()
    taxes = Constant.query.filter_by(libe='taxes').first()
    taxes_value = taxes.f_value if taxes else 1.13
    market_price = MarketPrice.query.filter_by(type_id=item.id).first()
    return render_template('items/show.html',
                           item=item,
                           jita=jita,
                           taxes=taxes_value,
                           market_price=market_price,
                           title=item.name)
