from flask import Blueprint, render_template, abort
from flask_login import current_user

from evebs.models import EveItem, TradeHub, Constant

bp = Blueprint('items', __name__)


@bp.route('/items/<slug>')
def show(slug):
    item = EveItem.find_by_slug(slug)
    if item is None:
        abort(404)
    jita = TradeHub.query.filter_by(eve_system_id=30000142).first()
    taxes = Constant.query.filter_by(libe='taxes').first()
    taxes_value = taxes.f_value if taxes else 1.13
    return render_template('items/show.html',
                           item=item,
                           jita=jita,
                           taxes=taxes_value,
                           title=item.name)
