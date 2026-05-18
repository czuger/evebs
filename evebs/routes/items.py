from flask import Blueprint, render_template, abort
from flask_login import current_user
from sqlalchemy.orm import joinedload

from evebs.models import TradeHub, Constant, UniverseType, MarketPrice, MarketOrder, UniverseSystem, UniverseStation

bp = Blueprint('items', __name__)


@bp.route('/items/<id>')
def show(id):
    """Render the item detail page with ESI prices and nearby market orders."""
    item = UniverseType.query.get(id)
    if item is None:
        abort(404)
    jita = TradeHub.query.filter_by(eve_system_id=30000142).first()
    taxes = Constant.query.filter_by(libe='taxes').first()
    taxes_value = taxes.f_value if taxes else 1.13
    market_price = MarketPrice.query.filter_by(type_id=item.id).first()

    sellers = []
    buyers = []
    current_station = None
    nearby_info = {}

    from flask import request as _req
    effective_max_jumps = _req.args.get('max_jumps', None, type=int)

    if current_user.is_authenticated and current_user.user_location_station:
        from evebs.engine.routing import find_systems_within_jumps
        current_station = current_user.user_location_station
        if effective_max_jumps is None:
            effective_max_jumps = current_user.max_jumps
        system = current_station.universe_system

        if system:
            nearby_info = find_systems_within_jumps(
                system.name,
                max_jumps=effective_max_jumps,
                avoid_lowsec=current_user.avoid_low_sec,
                avoid_nullsec=current_user.avoid_null_sec,
            )
            nearby_system_ids = [
                s.id for s in UniverseSystem.query.filter(
                    UniverseSystem.name.in_(nearby_info.keys())
                ).all()
            ]

            sellers = (MarketOrder.query
                       .options(joinedload(MarketOrder.universe_system))
                       .filter(
                           MarketOrder.is_buy_order == False,  # noqa: E712
                           MarketOrder.type_id == item.id,
                           MarketOrder.system_id.in_(nearby_system_ids),
                       )
                       .order_by(MarketOrder.price.asc())
                       .limit(10)
                       .all())

            buyers = (MarketOrder.query
                      .options(joinedload(MarketOrder.universe_system))
                      .filter(
                          MarketOrder.is_buy_order == True,  # noqa: E712
                          MarketOrder.type_id == item.id,
                          MarketOrder.system_id.in_(nearby_system_ids),
                      )
                      .order_by(MarketOrder.price.desc())
                      .limit(10)
                      .all())

    loc_ids = {o.location_id for o in sellers + buyers}
    stations_by_id = {
        s.id: s
        for s in UniverseStation.query.filter(UniverseStation.id.in_(loc_ids)).all()
    } if loc_ids else {}

    return render_template('items/show.html',
                           item=item,
                           jita=jita,
                           taxes=taxes_value,
                           market_price=market_price,
                           current_station=current_station,
                           sellers=sellers,
                           buyers=buyers,
                           stations_by_id=stations_by_id,
                           nearby_info=nearby_info,
                           effective_max_jumps=effective_max_jumps,
                           title=item.name)
