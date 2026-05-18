from flask import Blueprint, jsonify, render_template
from flask_login import current_user, login_required

bp = Blueprint('industry', __name__)


@bp.route('/industry/facilities/near/')
@login_required
def facilities_near():
    return render_template('industry/facilities_near.html',
                           title='Industry facilities near me')


@bp.route('/api/industry/facilities/near/')
@login_required
def api_facilities_near():
    station = current_user.user_location_station
    if not station or not station.universe_system:
        return jsonify({'error': 'No location set'}), 400

    from evebs.engine.industry import get_industry_facilities_near
    results = get_industry_facilities_near(
        station.universe_system.name,
        max_jumps=current_user.max_jumps,
        activity='manufacturing',
        avoid_lowsec=current_user.avoid_low_sec,
        avoid_nullsec=current_user.avoid_null_sec,
    )
    return jsonify(results)
