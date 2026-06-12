from flask import Blueprint as FlaskBlueprint, render_template, request, abort
from flask_login import login_required, current_user

from evebs.extensions import db
from evebs.models import UniverseSystem

bp = FlaskBlueprint('choose_trade_hubs', __name__)


@bp.route('/choose_trade_hubs/edit')
@login_required
def edit():
    user = current_user
    inner = (UniverseSystem.query
             .filter_by(trade_hub=True, is_inner=True)
             .order_by(UniverseSystem.name)
             .all())
    outer = (UniverseSystem.query
             .filter_by(trade_hub=True, is_inner=False)
             .order_by(UniverseSystem.name)
             .all())
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
    user = current_user
    trade_hub_id = request.form.get('id', type=int)
    check_state = request.form.get('check_state') == 'true'
    hub = db.session.get(UniverseSystem, trade_hub_id)
    if hub is None or not hub.trade_hub:
        abort(404)
    if check_state:
        if hub not in user.trade_hubs:
            user.trade_hubs.append(hub)
    else:
        if hub in user.trade_hubs:
            user.trade_hubs.remove(hub)
    db.session.commit()
    return ('', 200)
