from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from esi.client import EsiClient
from evebs.extensions import db
from evebs.models import UniverseStation

bp = Blueprint('users', __name__)


@bp.route('/users/edit')
@login_required
def edit():
    station = None
    if current_user.current_location_station_id:
        station = db.session.get(UniverseStation, current_user.current_location_station_id)
    return render_template('users/edit.html',
                           title='Editing user',
                           user=current_user,
                           current_station=station)


@bp.route('/users', methods=['POST'])
@login_required
def update():
    user = current_user

    raw_amount = request.form.get('min_amount_for_advice', '')
    raw_amount = raw_amount.replace(' ', '')
    raw_margin = request.form.get('sales_orders_show_margin_min', '').strip()

    try:
        user.min_pcent_for_advice = int(request.form.get('min_pcent_for_advice', user.min_pcent_for_advice))
        user.min_amount_for_advice = int(raw_amount) if raw_amount else user.min_amount_for_advice
        user.vol_month_pcent = int(request.form.get('vol_month_pcent', user.vol_month_pcent))
        user.batch_cap = request.form.get('batch_cap') == 'on'
        user.batch_cap_multiplier = int(request.form.get('batch_cap_multiplier', user.batch_cap_multiplier))
        user.watch_my_prices = request.form.get('watch_my_prices') == 'on'
        user.remove_occuped_places = request.form.get('remove_occuped_places') == 'on'
        user.sales_orders_show_margin_min = int(raw_margin) if raw_margin else None
    except (ValueError, TypeError):
        flash('Invalid input.')
        return redirect(url_for('users.edit'))

    db.session.commit()
    flash('User updated successfully.')
    return redirect(url_for('users.edit'))


@bp.route('/users/sync_location', methods=['POST'])
@login_required
def sync_location():
    client = EsiClient(rest_url=f'characters/{current_user.uid}/location/')
    if not client.set_auth_token(current_user):
        flash('No valid token — please sign in again.')
        return redirect(url_for('users.edit'))

    data = client.get_page()
    station_id = data.get('station_id') if data else None
    if not station_id:
        flash('Not docked at a station (in space or at a player structure).')
        return redirect(url_for('users.edit'))

    station = UniverseStation.query.filter_by(cpp_station_id=station_id).first()
    if not station:
        flash('Station not found in local database.')
        return redirect(url_for('users.edit'))

    if not station.name:
        info = EsiClient(rest_url=f'universe/stations/{station_id}/').get_page()
        if info and info.get('name'):
            station.name = info['name']

    current_user.current_location_station_id = station.id
    db.session.commit()
    flash(f'Location synced to {station.name or station.cpp_station_id}.')
    return redirect(url_for('users.edit'))
