from flask import Blueprint as FlaskBlueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from esi.client import EsiClient
from evebs.extensions import db
from evebs.models import (
    UniverseStation, UniverseSystem, UniverseStructure, UnknownStructure, UserAsset,
)

bp = FlaskBlueprint('users', __name__)


def _user_asset_locations(user_id):
    """The stations / known structures / unknown structures where a user holds assets."""
    stations = (UniverseStation.query
                .join(UserAsset, UserAsset.universe_station_id == UniverseStation.id)
                .filter(UserAsset.user_id == user_id).distinct().all())
    known_structures = (UniverseStructure.query
                        .join(UserAsset, UserAsset.universe_structure_id == UniverseStructure.id)
                        .filter(UserAsset.user_id == user_id).distinct().all())
    unknown_structures = (UnknownStructure.query
                          .join(UserAsset, UserAsset.universe_structure_id == UnknownStructure.id)
                          .filter(UserAsset.user_id == user_id).distinct().all())
    return stations, known_structures, unknown_structures


def _parse_taxes(form):
    """Build a User.industry_modifications dict from a submitted HTML form.

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
    }


def _parse_reaction_modifications(form):
    """Build a User.reaction_modifications dict from a submitted HTML form.

    system_cost_index / scc_tax / reaction_tax are plain percentages (5.0 = 5 %).
    material_consumption is a material-usage modifier that must be <= 0 (a reduction);
    any positive value is clamped to 0. Missing/non-numeric fields default to 0.0.
    """
    def pct(key):
        try:
            return float(form.get(key) or 0)
        except (ValueError, TypeError):
            return 0.0
    return {
        'system_cost_index':    pct('rxn_sci'),
        'scc_tax':              pct('rxn_scc'),
        'reaction_tax':         pct('rxn_tax'),
        'material_consumption': min(pct('rxn_material_consumption'), 0.0),
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
    raw_buy_margin_pcent = request.form.get('buy_min_margin_percent', '').strip()
    raw_buy_batch_margin = request.form.get('buy_min_batch_margin_amount', '').replace(' ', '')
    raw_buy_max_runs = request.form.get('buy_batch_cap_max_runs', '').strip()
    raw_margin = request.form.get('sales_orders_show_margin_min', '').strip()

    try:
        sof = user.sell_orders_filtering or {}
        user.sell_orders_filtering = {
            'min_margin_percent':      int(raw_margin_pcent) if raw_margin_pcent else sof.get('min_margin_percent', 20),
            'min_batch_margin_amount': int(raw_batch_margin) if raw_batch_margin else sof.get('min_batch_margin_amount', 5_000_000),
            'show_selected_items':     request.form.get('sell_show_selected_items') == 'on',
            'hide_low_confidence':     request.form.get('sell_hide_low_confidence') == 'on',
        }
        user.trade_route_filtering = {
            'buy_orders_only': request.form.get('trade_buy_orders_only') == 'on',
        }
        bof = user.buy_order_filtering or {}
        user.buy_order_filtering = {
            'min_margin_percent':      int(raw_buy_margin_pcent) if raw_buy_margin_pcent else bof.get('min_margin_percent', 20),
            'min_batch_margin_amount': int(raw_buy_batch_margin) if raw_buy_batch_margin else bof.get('min_batch_margin_amount', 5_000_000),
            'show_selected_items':     request.form.get('buy_show_selected_items') == 'on',
            'batch_cap':               request.form.get('buy_batch_cap') == 'on',
            'batch_cap_max_runs':      int(raw_buy_max_runs) if raw_buy_max_runs else bof.get('batch_cap_max_runs', 10),
        }
        user.watch_my_prices = request.form.get('watch_my_prices') == 'on'
        user.remove_occuped_places = request.form.get('remove_occuped_places') == 'on'
        user.sales_orders_show_margin_min = int(raw_margin) if raw_margin else None
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


@bp.route('/users/trade_hubs')
@login_required
def trade_hubs():
    user = current_user
    inner = (UniverseSystem.query
             .filter_by(trade_hub=True, is_inner=True)
             .order_by(UniverseSystem.name)
             .all())
    outer = (UniverseSystem.query
             .filter_by(trade_hub=True, is_inner=False)
             .order_by(UniverseSystem.name)
             .all())
    return render_template('users/trade_hubs.html',
                           title='Choose trade hubs to monitor',
                           inner_trade_hubs=inner,
                           outer_trade_hubs=outer,
                           user_trade_hubs_ids=set(user.trade_hub_ids),
                           user=user)


@bp.route('/users/trade_hubs/update', methods=['POST'])
@login_required
def update_trade_hubs():
    user = current_user
    trade_hub_id = request.form.get('id', type=int)
    check_state = request.form.get('check_state') == 'true'
    hub = db.session.get(UniverseSystem, trade_hub_id)
    if hub is None or not hub.trade_hub:
        abort(404)
    if check_state:
        if hub not in user.trade_hubs:
            user.trade_hubs.append(hub)
    elif hub in user.trade_hubs:
        user.trade_hubs.remove(hub)
    db.session.commit()
    return ('', 200)


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


@bp.route('/users/industry_modifications')
@login_required
def industry_modifications():
    stations, known_structures, unknown_structures = _user_asset_locations(current_user.id)
    return render_template('users/industry_modifications.html',
                           title='Industry modifications',
                           user=current_user,
                           stations=stations,
                           known_structures=known_structures,
                           unknown_structures=unknown_structures)


@bp.route('/users/industry_modifications', methods=['POST'])
@login_required
def update_industry_modifications():
    mods = _parse_taxes(request.form)
    mods['current_industry_station'] = request.form.get('current_industry_station', type=int)
    current_user.industry_modifications = mods
    db.session.commit()
    flash('Industry modifications updated.')
    return redirect(url_for('users.industry_modifications'))


@bp.route('/users/reaction_modifications')
@login_required
def reaction_modifications():
    return render_template('users/reaction_modifications.html',
                           title='Reaction modifications',
                           user=current_user)


@bp.route('/users/reaction_modifications', methods=['POST'])
@login_required
def update_reaction_modifications():
    current_user.reaction_modifications = _parse_reaction_modifications(request.form)
    db.session.commit()
    flash('Reaction modifications updated.')
    return redirect(url_for('users.reaction_modifications'))


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
