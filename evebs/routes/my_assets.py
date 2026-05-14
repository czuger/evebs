from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from evebs.extensions import db
from evebs.models import BpcAsset, UniverseStation

bp = Blueprint('my_assets', __name__)


@bp.route('/my_assets')
@login_required
def show():
    user = current_user
    assets = BpcAsset.query.filter_by(user_id=user.id).all()
    stations = UniverseStation.query.join(BpcAsset, BpcAsset.universe_station_id == UniverseStation.id).filter(
        BpcAsset.user_id == user.id
    ).distinct().all()
    return render_template('my_assets/show.html',
                           title='My assets',
                           assets=assets,
                           stations=stations,
                           user=user)


@bp.route('/my_assets/set_assets_station', methods=['POST'])
@login_required
def set_assets_station():
    station_id = request.form.get('station_id', type=int)
    current_user.selected_assets_station_id = station_id
    db.session.commit()
    return redirect(url_for('my_assets.show'))
