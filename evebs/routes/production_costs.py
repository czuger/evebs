from flask import Blueprint, render_template, abort, request, jsonify, flash
from flask_login import current_user, login_required

from evebs.extensions import db
from evebs.models import UniverseType, WeeklyPriceDetail

bp = Blueprint('production_costs', __name__)
PER_PAGE = 20


@bp.route('/production_costs/<int:type_id>')
def show(type_id):
    """Render the production cost breakdown for a crafted item."""
    from itertools import groupby
    from sqlalchemy.orm import joinedload
    from sqlalchemy import func
    from evebs.models import Blueprint, BlueprintMaterial, MarketSellerPrice, MarketBuyerPrice, BpcAsset, UniverseStation, UniverseSystem, MarketOrder
    from evebs.engine.routing import find_systems_within_jumps

    item = UniverseType.query.get(type_id)
    if item is None:
        abort(404)

    blueprint = (Blueprint.query
                 .filter_by(produced_type_id=type_id)
                 .options(joinedload(Blueprint.blueprint_materials)
                          .joinedload(BlueprintMaterial.universe_type))
                 .first())

    market_prices = {}
    result_mp = None
    owned_quantities = {}
    current_station = None
    output_buyers = []
    input_sellers = {}
    trade_hub_regions = []

    cheapest_facility = None
    tax_rate = 0.0

    if blueprint:
        mat_type_ids = [m.universe_type_id for m in blueprint.blueprint_materials]
        market_prices = {
            sp.type_id: sp
            for sp in MarketSellerPrice.query.filter(
                MarketSellerPrice.type_id.in_(mat_type_ids),
                MarketSellerPrice.system_id == 30000142,
            ).all()
        }
        result_mp = MarketBuyerPrice.query.filter_by(
            type_id=type_id, system_id=30000142
        ).first()
        if current_user.is_authenticated:
            rows = (
                db.session.query(BpcAsset.eve_item_id, func.sum(BpcAsset.quantity))
                .filter(
                    BpcAsset.user_id == current_user.id,
                    BpcAsset.eve_item_id.in_(mat_type_ids),
                )
                .group_by(BpcAsset.eve_item_id)
                .all()
            )
            owned_quantities = {eve_item_id: int(total) for eve_item_id, total in rows}

            # Determine current station: station with highest Σ(owned_qty × material.volume)
            mat_volumes = {
                m.universe_type_id: (m.universe_type.volume or 0)
                for m in blueprint.blueprint_materials
                if m.universe_type
            }
            asset_rows = (
                BpcAsset.query
                .options(
                    joinedload(BpcAsset.universe_station)
                    .joinedload(UniverseStation.universe_system)
                )
                .filter(
                    BpcAsset.user_id == current_user.id,
                    BpcAsset.eve_item_id.in_(mat_type_ids),
                    BpcAsset.universe_station_id.isnot(None),
                )
                .all()
            )
            station_scores = {}
            station_objects = {}
            for asset in asset_rows:
                vol = mat_volumes.get(asset.eve_item_id, 0)
                sid = asset.universe_station_id
                station_scores[sid] = station_scores.get(sid, 0) + asset.quantity * vol
                station_objects[sid] = asset.universe_station

            if station_scores:
                best_sid = max(station_scores, key=station_scores.__getitem__)
                current_station = station_objects[best_sid]

            if current_station and current_station.universe_system:
                from evebs.engine.industry import get_industry_facilities_near
                facilities = get_industry_facilities_near(
                    current_station.universe_system.name,
                    max_jumps=current_user.max_jumps,
                    activity='manufacturing',
                    avoid_lowsec=current_user.avoid_low_sec,
                    avoid_nullsec=current_user.avoid_null_sec,
                )
                if facilities:
                    cheapest_facility = facilities[0]
                    cost_index = cheapest_facility['cost_index']
                    tax_rate = (cost_index
                               + current_user.facility_tax / 100
                               + current_user.scc_surcharge / 100)

                nearby_info = find_systems_within_jumps(
                    current_station.universe_system.name,
                    max_jumps=5,
                    avoid_lowsec=True,
                    avoid_nullsec=True,
                )
                nearby_system_ids = [
                    s.id for s in UniverseSystem.query.filter(
                        UniverseSystem.name.in_(nearby_info.keys())
                    ).all()
                ]

                output_buyers = (
                    MarketOrder.query
                    .options(joinedload(MarketOrder.universe_system))
                    .filter(
                        MarketOrder.is_buy_order == True,  # noqa: E712
                        MarketOrder.type_id == type_id,
                        MarketOrder.system_id.in_(nearby_system_ids),
                    )
                    .order_by(MarketOrder.price.desc())
                    .limit(20)
                    .all()
                )

                raw_sellers = (
                    MarketOrder.query
                    .options(joinedload(MarketOrder.universe_system))
                    .filter(
                        MarketOrder.is_buy_order == False,  # noqa: E712
                        MarketOrder.type_id.in_(mat_type_ids),
                        MarketOrder.system_id.in_(nearby_system_ids),
                    )
                    .order_by(MarketOrder.type_id, MarketOrder.price.asc())
                    .all()
                )
                for tid, grp in groupby(raw_sellers, key=lambda o: o.type_id):
                    input_sellers[tid] = list(grp)[:3]

                # Derive regions from every system shown in the order tables
                from evebs.models import UniverseConstellation, UniverseRegion
                const_ids = set()
                for o in output_buyers:
                    if o.universe_system and o.universe_system.universe_constellation_id:
                        const_ids.add(o.universe_system.universe_constellation_id)
                for orders in input_sellers.values():
                    for o in orders:
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

    from evebs.models import IndustryInterestingItem
    interesting_region_ids = {
        r.region_id for r in IndustryInterestingItem.query.filter_by(item_id=type_id).all()
    }

    return render_template('production_costs/show.html',
                           item=item,
                           blueprint=blueprint,
                           market_prices=market_prices,
                           result_mp=result_mp,
                           owned_quantities=owned_quantities,
                           tax_rate=tax_rate,
                           cheapest_facility=cheapest_facility,
                           current_station=current_station,
                           output_buyers=output_buyers,
                           input_sellers=input_sellers,
                           interesting_region_ids=interesting_region_ids,
                           trade_hub_regions=trade_hub_regions,
                           title=f'Production cost — {item.name}')


@bp.route('/production_costs/<int:type_id>/mark_interesting', methods=['POST'])
@login_required
def mark_interesting(type_id):
    """Bulk-save all (region_id, type_id) combinations posted; ignore duplicates."""
    from flask import redirect, url_for
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
    return redirect(url_for('production_costs.show', type_id=type_id))


@bp.route('/production_costs/<item_slug>/dailies_avg_prices/<int:trade_hub_id>')  # legacy
def dailies_avg_prices(item_slug, trade_hub_id):
    """Render the weekly average price history for a base material."""
    item = UniverseType.find_by_slug(item_slug)
    if item is None:
        abort(404)
    if not item.base_item:
        abort(400)
    page = request.args.get('page', 1, type=int)
    q = WeeklyPriceDetail.query.filter_by(
        eve_item_id=item.id,
        trade_hub_id=trade_hub_id,
    ).order_by(WeeklyPriceDetail.day.desc())
    pagination = q.paginate(page=page, per_page=PER_PAGE)
    return render_template('production_costs/dailies_avg_prices.html',
                           item=item,
                           dailies_details=pagination.items,
                           pagination=pagination,
                           title=f'Weekly average price detail for {item.name}')


@bp.route('/production_costs/<slug>/market_histories')  # legacy
def market_histories(slug):
    """Render regional market history stats for an item."""
    from evebs.models import EveMarketHistoriesGroup  # noqa: F401
    from sqlalchemy.orm import joinedload
    item = UniverseType.find_by_slug(slug)
    if item is None:
        abort(404)
    histories = (EveMarketHistoriesGroup.query
                 .filter_by(eve_item_id=item.id)
                 .join(EveMarketHistoriesGroup.universe_region)
                 .order_by(EveMarketHistoriesGroup.volume.desc())
                 .all())
    return render_template('production_costs/market_histories.html',
                           item=item,
                           market_histories=histories,
                           title=f'Regional information about {item.name}')
