from flask import Blueprint, render_template, request, abort
from flask_login import current_user, login_required

bp = Blueprint('planetary', __name__)


@bp.route('/planetary/advice')
@login_required
def advice():
    station = current_user.user_location_station
    system_name = station.universe_system.name if station and station.universe_system else None

    max_jumps = request.args.get('max_jumps', current_user.max_jumps, type=int)

    results = []
    if system_name:
        from evebs.engine.planetary import get_planetary_advice
        results = get_planetary_advice(
            origin_system_name=system_name,
            max_jumps=max_jumps,
            avoid_lowsec=current_user.avoid_low_sec,
            avoid_nullsec=current_user.avoid_null_sec,
        )

    return render_template(
        'planetary/advice.html',
        results=results,
        system_name=system_name,
        max_jumps=max_jumps,
    )


@bp.route('/planetary/systems/<int:type_id>')
@login_required
def systems(type_id):
    station = current_user.user_location_station
    system_name = station.universe_system.name if station and station.universe_system else None

    max_jumps = request.args.get('max_jumps', current_user.max_jumps, type=int)

    if not system_name:
        abort(404)

    from evebs.engine.planetary import get_planetary_advice
    all_results = get_planetary_advice(
        origin_system_name=system_name,
        max_jumps=max_jumps,
        avoid_lowsec=current_user.avoid_low_sec,
        avoid_nullsec=current_user.avoid_null_sec,
    )

    result = next((r for r in all_results if r['output_type_id'] == type_id), None)
    if result is None:
        abort(404)

    return render_template(
        'planetary/systems.html',
        result=result,
        system_name=system_name,
        max_jumps=max_jumps,
    )
