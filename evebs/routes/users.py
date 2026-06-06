from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from esi.client import EsiClient
from evebs.extensions import db
from evebs.models import UniverseStation

bp = Blueprint('users', __name__)


def _parse_taxes(form):
    """Build a User.industry_taxes dict from a submitted HTML form.

    Each activity section in the settings form uses short field-name prefixes to
    avoid collisions (mfg_ = manufacturing, cpy_ = copying, inv_ = invention,
    mer_ = material research, ter_ = time research, rxn_ = reaction).

    Suffix meanings:
      _sci  → system_cost_index  (CCP per-system rate, plain %)
      _scc  → scc_tax            (Secure Commerce Commission surcharge, plain %)
      _std  → standard_tax       (manufacturing: normal job tax, plain %)
      _cap  → capital_tax        (manufacturing: capital ship job tax, plain %)
      _tax  → activity-specific tax for all other activities (plain %)

    All values are stored as plain percentages (5.0 = 5 %).
    Missing or non-numeric fields default to 0.0 — the caller is responsible
    for deciding whether to overwrite an existing value or keep the old one.
    """
    def pct(key):
        try:
            return float(form.get(key) or 0)
        except (ValueError, TypeError):
            return 0.0
    return {
        'manufacturing':     {'system_cost_index': pct('mfg_sci'), 'scc_tax': pct('mfg_scc'), 'standard_tax': pct('mfg_std'), 'capital_tax': pct('mfg_cap')},
        'material_research': {'system_cost_index': pct('mer_sci'), 'scc_tax': pct('mer_scc'), 'material_tax': pct('mer_tax')},
        'time_research':     {'system_cost_index': pct('ter_sci'), 'scc_tax': pct('ter_scc'), 'time_tax': pct('ter_tax')},
        'copying':           {'system_cost_index': pct('cpy_sci'), 'scc_tax': pct('cpy_scc'), 'copying_tax': pct('cpy_tax')},
        'invention':         {'system_cost_index': pct('inv_sci'), 'scc_tax': pct('inv_scc'), 'invention_tax': pct('inv_tax')},
        'reaction':          {'system_cost_index': pct('rxn_sci'), 'scc_tax': pct('rxn_scc'), 'reaction_tax': pct('rxn_tax')},
    }


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

    raw_margin_pcent = request.form.get('min_margin_percent', '').strip()
    raw_batch_margin = request.form.get('min_batch_margin_amount', '').replace(' ', '')
    raw_margin = request.form.get('sales_orders_show_margin_min', '').strip()

    try:
        sof = user.sell_orders_filtering or {}
        user.sell_orders_filtering = {
            'min_margin_percent':      int(raw_margin_pcent) if raw_margin_pcent else sof.get('min_margin_percent', 20),
            'min_batch_margin_amount': int(raw_batch_margin) if raw_batch_margin else sof.get('min_batch_margin_amount', 5_000_000),
        }
        user.batch_cap = request.form.get('batch_cap') == 'on'
        user.batch_cap_multiplier = int(request.form.get('batch_cap_multiplier', user.batch_cap_multiplier))
        user.watch_my_prices = request.form.get('watch_my_prices') == 'on'
        user.remove_occuped_places = request.form.get('remove_occuped_places') == 'on'
        user.sales_orders_show_margin_min = int(raw_margin) if raw_margin else None
        user.industry_taxes = _parse_taxes(request.form)
    except (ValueError, TypeError):
        flash('Invalid input.')
        return redirect(url_for('users.edit'))

    db.session.commit()
    flash('User updated successfully.')
    return redirect(url_for('users.edit'))


def _parse_sales_taxes(form):
    """Build a User.sales_taxes dict from a submitted HTML form.

    Fields: broker_fee_taxes, sales_taxes, safety_tax — all plain percentages (e.g. 2.0 = 2 %).
    Missing or non-numeric fields default to 0.0.
    """
    def pct(key):
        try:
            return float(form.get(key) or 0)
        except (ValueError, TypeError):
            return 0.0
    return {
        'broker_fee_taxes': pct('broker_fee_taxes'),
        'sales_taxes':      pct('sales_taxes'),
        'safety_tax':       pct('safety_tax'),
    }


@bp.route('/users/sales_taxes')
@login_required
def sales_taxes():
    return render_template('users/sales_taxes.html', title='Sales taxes', user=current_user)


@bp.route('/users/sales_taxes', methods=['POST'])
@login_required
def update_sales_taxes():
    current_user.sales_taxes = _parse_sales_taxes(request.form)
    db.session.commit()
    flash('Sales taxes updated.')
    return redirect(url_for('users.sales_taxes'))


@bp.route('/users/industry_taxes')
@login_required
def industry_taxes():
    return render_template('users/industry_taxes.html',
                           title='Industry taxes',
                           user=current_user)


@bp.route('/users/industry_taxes', methods=['POST'])
@login_required
def update_industry_taxes():
    current_user.industry_taxes = _parse_taxes(request.form)
    db.session.commit()
    flash('Industry taxes updated.')
    return redirect(url_for('users.industry_taxes'))


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

    station = db.session.get(UniverseStation, station_id)
    if not station:
        flash('Station not found in local database.')
        return redirect(url_for('users.edit'))

    if not station.name:
        info = EsiClient(rest_url=f'universe/stations/{station_id}/').get_page()
        if info and info.get('name'):
            station.name = info['name']

    current_user.current_location_station_id = station.id
    db.session.commit()
    flash(f'Location synced to {station.name or station.id}.')
    return redirect(url_for('users.edit'))
