from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from evebs.extensions import db
from evebs.models import UniverseSystem

bp = Blueprint('choose_trade_hubs', __name__)


@bp.route('/choose_trade_hubs/edit')
@login_required
def edit():
    """Render the trade hub selection form."""
    user = current_user
    hubs = UniverseSystem.query.filter_by(trade_hub=True).order_by(UniverseSystem.name).all()
    user_hub_ids = set(user.trade_hub_ids)
    return render_template('choose_trade_hubs/edit.html',
                           title='Choose trade hubs to monitor',
                           trade_hubs=hubs,
                           user_trade_hubs_ids=user_hub_ids,
                           user=user)


@bp.route('/choose_trade_hubs/update', methods=['POST'])
@login_required
def update():
    """Toggle a trade hub in the user's watchlist via AJAX."""
    user = current_user
    system_id = request.form.get('id', type=int)
    check_state = request.form.get('check_state') == 'true'
    system = UniverseSystem.query.get_or_404(system_id)
    if check_state:
        if system not in user.universe_systems:
            user.universe_systems.append(system)
    else:
        if system in user.universe_systems:
            user.universe_systems.remove(system)
    db.session.commit()
    return ('', 200)
