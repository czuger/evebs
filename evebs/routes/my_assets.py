from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from evebs.extensions import db
from sqlalchemy.orm import joinedload
from evebs.models import BpcAsset, UniverseStation, MarketPrice

bp = Blueprint('my_assets', __name__)


@bp.route('/my_assets')
@login_required
def show():
    """Display the current user's BPC assets, optionally filtered by station."""
    user = current_user

    # Assets filtered by selected station if one is set
    from evebs.models import UniverseType
    q = (BpcAsset.query
         .options(joinedload(BpcAsset.universe_type), joinedload(BpcAsset.universe_station))
         .join(BpcAsset.universe_type)
         .filter(BpcAsset.user_id == user.id)
         .order_by(UniverseType.name))
    if user.selected_assets_station_id:
        q = q.filter(BpcAsset.universe_station_id == user.selected_assets_station_id)
    assets = q.all()

    type_ids = [a.eve_item_id for a in assets if a.eve_item_id]
    market_prices = {
        mp.type_id: mp
        for mp in MarketPrice.query.filter(MarketPrice.type_id.in_(type_ids)).all()
    }

    def asset_value(a):
        mp = market_prices.get(a.eve_item_id)
        return (mp.average_price or 0) * a.quantity if mp else 0

    assets = sorted(assets, key=asset_value, reverse=True)

    # All distinct stations the user has assets at (for the station selector)
    station_ids = (db.session.query(BpcAsset.universe_station_id)
                   .filter_by(user_id=user.id)
                   .filter(BpcAsset.universe_station_id.isnot(None))
                   .distinct())
    stations = UniverseStation.query.filter(UniverseStation.id.in_(station_ids)).all()
    return render_template('my_assets/show.html',
                           title='My assets',
                           assets=assets,
                           market_prices=market_prices,
                           stations=stations,
                           user=user)


@bp.route('/my_assets/set_assets_station', methods=['POST'])
@login_required
def set_assets_station():
    """Persist the user's selected station filter."""
    station_id = request.form.get('station_id', type=int)
    current_user.selected_assets_station_id = station_id
    db.session.commit()
    return redirect(url_for('my_assets.show'))
