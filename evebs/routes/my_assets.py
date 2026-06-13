import os
import subprocess
import sys

import redis as redis_lib
from flask import Blueprint as FlaskBlueprint, render_template, request, redirect, url_for, current_app, jsonify, flash
from flask_login import login_required, current_user

from evebs.extensions import db
from evebs.models import UserAsset, EveItem, UniverseStation, UniverseStructure, UnknownStructure

bp = FlaskBlueprint('my_assets', __name__)


def _redis():
    return redis_lib.from_url(current_app.config['REDIS_URL'])


def _sync_key(user_id):
    return f'assets_sync:{user_id}'


def _error_key(user_id):
    return f'assets_sync_error:{user_id}'


@bp.before_app_request
def _flash_asset_sync_error():
    """Surface a failed background asset sync (recorded in Redis by sync_assets.py) as a
    one-time flash on the user's next request, since the subprocess can't warn the UI."""
    if not current_user.is_authenticated:
        return
    try:
        r = _redis()
        key = _error_key(current_user.id)
        msg = r.get(key)
        if msg:
            r.delete(key)
            flash(f'Asset sync failed: {msg.decode()}', 'error')
    except redis_lib.RedisError:
        pass


def _location_label(station, structure, unknown):
    if station:
        return station.name or str(station.id)
    if structure:
        return structure.name
    if unknown:
        return unknown.name
    return '—'


def _build_groups(rows):
    """Transform flat query rows into location→container hierarchy for the template."""
    item_name_by_esi_id = {
        bpc.esi_item_id: item.name
        for bpc, item, *_ in rows
        if bpc.esi_item_id is not None
    }

    loc_order = []
    loc_seen = {}
    for bpc, item, station, structure, unknown in rows:
        loc = _location_label(station, structure, unknown)
        if loc not in loc_seen:
            loc_seen[loc] = {'label': loc, '_containers': {}}
            loc_order.append(loc)
        container_label = (
            item_name_by_esi_id.get(bpc.parent_esi_item_id)
            if bpc.parent_esi_item_id else None
        )
        containers = loc_seen[loc]['_containers']
        if container_label not in containers:
            containers[container_label] = []
        containers[container_label].append((bpc, item))

    result = []
    for loc in loc_order:
        containers = loc_seen[loc]['_containers']
        groups = []
        if None in containers:
            groups.append({'container': None, 'rows': containers[None]})
        for cname in sorted(k for k in containers if k is not None):
            groups.append({'container': cname, 'rows': containers[cname]})
        result.append({'label': loc, 'groups': groups})
    return result


@bp.route('/my_assets')
@login_required
def show():
    user = current_user
    location_id = request.args.get('location_id', type=int)

    query = (
        db.session.query(UserAsset, EveItem, UniverseStation, UniverseStructure, UnknownStructure)
        .join(EveItem, UserAsset.eve_item_id == EveItem.id)
        .outerjoin(UniverseStation, UserAsset.universe_station_id == UniverseStation.id)
        .outerjoin(UniverseStructure, UserAsset.universe_structure_id == UniverseStructure.id)
        .outerjoin(UnknownStructure, UserAsset.universe_structure_id == UnknownStructure.id)
        .filter(UserAsset.user_id == user.id)
    )
    if location_id:
        query = query.filter(
            (UserAsset.universe_station_id == location_id) |
            (UserAsset.universe_structure_id == location_id)
        )
    rows = query.order_by(
        UserAsset.universe_station_id.nulls_last(),
        UserAsset.universe_structure_id.nulls_last(),
        UserAsset.parent_esi_item_id.nulls_first(),
        EveItem.name,
    ).all()

    locations = _build_groups(rows)

    stations = (
        UniverseStation.query
        .join(UserAsset, UserAsset.universe_station_id == UniverseStation.id)
        .filter(UserAsset.user_id == user.id)
        .distinct().all()
    )
    known_structures = (
        UniverseStructure.query
        .join(UserAsset, UserAsset.universe_structure_id == UniverseStructure.id)
        .filter(UserAsset.user_id == user.id)
        .distinct().all()
    )
    unknown_structures = (
        UnknownStructure.query
        .join(UserAsset, UserAsset.universe_structure_id == UnknownStructure.id)
        .filter(UserAsset.user_id == user.id)
        .distinct().all()
    )

    sync_running = _redis().get(_sync_key(user.id)) == b'running'

    return render_template('my_assets/show.html',
                           title='My assets',
                           locations=locations,
                           stations=stations,
                           known_structures=known_structures,
                           unknown_structures=unknown_structures,
                           selected_location_id=location_id,
                           sync_running=sync_running,
                           user=user)


@bp.route('/my_assets/sync', methods=['POST'])
@login_required
def sync():
    r = _redis()
    key = _sync_key(current_user.id)
    if r.get(key) == b'running':
        return jsonify({'status': 'already_running'})
    script = os.path.join(
        os.path.dirname(current_app.root_path), 'process', 'sync_assets.py'
    )
    subprocess.Popen(
        [sys.executable, script, '--user-id', str(current_user.id)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
    )
    r.set(key, 'running', ex=300)
    return jsonify({'status': 'started'})


@bp.route('/my_assets/sync_status')
@login_required
def sync_status():
    val = _redis().get(_sync_key(current_user.id))
    return jsonify({'status': val.decode() if val else 'idle'})


@bp.route('/my_assets/set_assets_station', methods=['POST'])
@login_required
def set_assets_station():
    station_id = request.form.get('station_id', type=int)
    current_user.selected_assets_station_id = station_id
    db.session.commit()
    return redirect(url_for('my_assets.show'))
