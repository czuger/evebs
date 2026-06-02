from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

from esi.download_my_assets import DownloadMyAssets
from evebs.extensions import db
from evebs.models import BpcAsset, EveItem, UniverseStation, UniverseStructure, UnknownStructure

bp = Blueprint('my_assets', __name__)

PER_PAGE = 20


@bp.route('/my_assets')
@login_required
def show():
    user = current_user
    page = request.args.get('page', 1, type=int)
    location_id = request.args.get('location_id', type=int)

    query = (
        db.session.query(BpcAsset, EveItem, UniverseStation, UniverseStructure, UnknownStructure)
        .join(EveItem, BpcAsset.eve_item_id == EveItem.id)
        .outerjoin(UniverseStation, BpcAsset.universe_station_id == UniverseStation.id)
        .outerjoin(UniverseStructure, BpcAsset.universe_structure_id == UniverseStructure.id)
        .outerjoin(UnknownStructure, BpcAsset.universe_structure_id == UnknownStructure.id)
        .filter(BpcAsset.user_id == user.id)
    )
    if location_id:
        query = query.filter(
            (BpcAsset.universe_station_id == location_id) |
            (BpcAsset.universe_structure_id == location_id)
        )
    pagination = query.order_by(EveItem.name).paginate(page=page, per_page=PER_PAGE)

    stations = (
        UniverseStation.query
        .join(BpcAsset, BpcAsset.universe_station_id == UniverseStation.id)
        .filter(BpcAsset.user_id == user.id)
        .distinct().all()
    )
    known_structures = (
        UniverseStructure.query
        .join(BpcAsset, BpcAsset.universe_structure_id == UniverseStructure.id)
        .filter(BpcAsset.user_id == user.id)
        .distinct().all()
    )
    unknown_structures = (
        UnknownStructure.query
        .join(BpcAsset, BpcAsset.universe_structure_id == UnknownStructure.id)
        .filter(BpcAsset.user_id == user.id)
        .distinct().all()
    )
    return render_template('my_assets/show.html',
                           title='My assets',
                           assets=pagination.items,
                           pagination=pagination,
                           stations=stations,
                           known_structures=known_structures,
                           unknown_structures=unknown_structures,
                           selected_location_id=location_id,
                           user=user)


@bp.route('/my_assets/sync', methods=['POST'])
@login_required
def sync():
    current_user.download_assets_running = True
    db.session.commit()
    DownloadMyAssets().update(current_user)
    flash('Assets synced.')
    return redirect(url_for('my_assets.show'))


@bp.route('/my_assets/set_assets_station', methods=['POST'])
@login_required
def set_assets_station():
    station_id = request.form.get('station_id', type=int)
    current_user.selected_assets_station_id = station_id
    db.session.commit()
    return redirect(url_for('my_assets.show'))
