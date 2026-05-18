from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from evebs.extensions import db
from evebs.models import TradeHub

bp = Blueprint('choose_trade_hubs', __name__)


@bp.route('/choose_trade_hubs/edit')
@login_required
def edit():
    """Render the trade hub selection form."""
    user = current_user
    inner = TradeHub.query.filter_by(inner=True).join(TradeHub.universe_region).order_by(TradeHub.name).all()
    inner = [th for th in inner if th.universe_region is not None]
    outer = TradeHub.query.filter_by(inner=False).join(TradeHub.universe_region).order_by(TradeHub.name).all()
    outer = [th for th in outer if th.universe_region is not None]
    user_hub_ids = set(user.trade_hub_ids)
    return render_template('choose_trade_hubs/edit.html',
                           title='Choose trade hubs to monitor',
                           inner_trade_hubs=inner,
                           outer_trade_hubs=outer,
                           user_trade_hubs_ids=user_hub_ids,
                           user=user)


@bp.route('/choose_trade_hubs/update', methods=['POST'])
@login_required
def update():
    """Toggle a trade hub in the user's watchlist via AJAX."""
    user = current_user
    trade_hub_id = request.form.get('id', type=int)
    check_state = request.form.get('check_state') == 'true'
    hub = TradeHub.query.get_or_404(trade_hub_id)
    if check_state:
        if hub not in user.trade_hubs:
            user.trade_hubs.append(hub)
    else:
        if hub in user.trade_hubs:
            user.trade_hubs.remove(hub)
    db.session.commit()
    return ('', 200)
