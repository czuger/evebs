from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from evebs.extensions import db

bp = Blueprint('users', __name__)


@bp.route('/users/edit')
@login_required
def edit():
    """Render the user settings form."""
    return render_template('users/edit.html',
                           title='Settings',
                           user=current_user)


@bp.route('/users', methods=['POST'])
@login_required
def update():
    """Persist user preference changes."""
    user = current_user

    raw_amount = request.form.get('min_amount_for_advice', '')
    raw_amount = raw_amount.replace(' ', '')

    try:
        user.min_pcent_for_advice = int(request.form.get('min_pcent_for_advice', user.min_pcent_for_advice))
        user.min_amount_for_advice = int(raw_amount) if raw_amount else user.min_amount_for_advice
        user.vol_month_pcent = int(request.form.get('vol_month_pcent', user.vol_month_pcent))
        user.batch_cap = request.form.get('batch_cap') == 'on'
        user.batch_cap_multiplier = int(request.form.get('batch_cap_multiplier', user.batch_cap_multiplier))
        user.avoid_low_sec = request.form.get('avoid_low_sec') == 'on'
        user.avoid_null_sec = request.form.get('avoid_null_sec') == 'on'
        user.max_jumps = int(request.form.get('max_jumps', user.max_jumps))
        user.facility_tax = float(request.form.get('facility_tax', user.facility_tax))
        user.scc_surcharge = float(request.form.get('scc_surcharge', user.scc_surcharge))
    except (ValueError, TypeError):
        flash('Invalid input.')
        return redirect(url_for('users.edit'))

    db.session.commit()
    flash('Settings saved.')
    return redirect(url_for('users.edit'))


@bp.route('/users/refresh_location', methods=['POST'])
@login_required
def refresh_location():
    """Fetch the character's current location from ESI and store the station if applicable."""
    from esi.client import EsiClient

    client = EsiClient(f'characters/{current_user.uid}/location/')
    if not client.set_auth_token(current_user):
        flash('Token expired — please log in again.')
        return redirect(url_for('users.edit'))

    location = client.get_page()
    station_id = (location or {}).get('station_id')

    if station_id:
        current_user.user_location_station_id = station_id
        db.session.commit()
        flash('Location updated.')
    else:
        flash('You are docked in a structure — location not stored.')

    return redirect(url_for('users.edit'))
