from flask import Blueprint, render_template, abort, request, flash, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from evebs.extensions import db
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

    effective_max_jumps = request.args.get('max_jumps', None, type=int)

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

    trade_hub_regions = []
    if sellers or buyers:
        from evebs.models import UniverseConstellation, UniverseRegion
        const_ids = set()
        for o in sellers + buyers:
            if o.universe_system and o.universe_system.universe_constellation_id:
                const_ids.add(o.universe_system.universe_constellation_id)
        if const_ids:
            consts = UniverseConstellation.query.filter(
                UniverseConstellation.id.in_(const_ids)
            ).all()
            region_ids_set = {c.universe_region_id for c in consts if c.universe_region_id}
            if region_ids_set:
                trade_hub_regions = [
                    (r.id, r.name)
                    for r in UniverseRegion.query
                    .filter(UniverseRegion.id.in_(region_ids_set))
                    .order_by(UniverseRegion.name).all()
                ]

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
                           trade_hub_regions=trade_hub_regions,
                           title=item.name)


@bp.route('/items/<int:item_id>/mark_interesting', methods=['POST'])
@login_required
def mark_interesting(item_id):
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    from evebs.models import IndustryInterestingItem
    region_ids = [int(x) for x in request.form.getlist('region_id') if x]
    type_ids = [int(x) for x in request.form.getlist('type_id') if x]
    if region_ids and type_ids:
        rows = [{'region_id': rid, 'item_id': tid} for rid in region_ids for tid in type_ids]
        db.session.execute(
            pg_insert(IndustryInterestingItem).values(rows).on_conflict_do_nothing()
        )
        db.session.commit()
        flash(f'{len(type_ids)} item(s) marked as interesting across {len(region_ids)} region(s).')
    max_jumps = request.form.get('max_jumps', type=int)
    return redirect(url_for('items.show', id=item_id, max_jumps=max_jumps) if max_jumps
                    else url_for('items.show', id=item_id))
