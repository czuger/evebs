from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import func

from evebs.extensions import db
from evebs.models import ComponentToBuy, BpcAsset, UniverseStation, UniverseStructure, UnknownStructure

bp = Blueprint('components_to_buys', __name__)


@bp.route('/components_to_buys')
@login_required
def show():
    user = current_user
    station_id = request.args.get('station_id', type=int)

    components = ComponentToBuy.query.filter_by(user_id=user.id).all()

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

    asset_qty = {}
    if station_id:
        rows = (
            db.session.query(BpcAsset.eve_item_id, func.sum(BpcAsset.quantity))
            .filter(
                BpcAsset.user_id == user.id,
                db.or_(
                    BpcAsset.universe_station_id == station_id,
                    BpcAsset.universe_structure_id == station_id,
                ),
            )
            .group_by(BpcAsset.eve_item_id)
            .all()
        )
        asset_qty = {row[0]: int(row[1]) for row in rows}

    return render_template('components_to_buys/show.html',
                           title='Components to buy',
                           components=components,
                           stations=stations,
                           known_structures=known_structures,
                           unknown_structures=unknown_structures,
                           selected_station_id=station_id,
                           asset_qty=asset_qty,
                           user=user)
