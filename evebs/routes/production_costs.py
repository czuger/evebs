from flask import Blueprint, render_template, abort, request
from flask_login import current_user

from evebs.extensions import db
from evebs.models import UniverseType, Constant, TradeHub, WeeklyPriceDetail

bp = Blueprint('production_costs', __name__)
PER_PAGE = 20


@bp.route('/production_costs/<int:type_id>')
def show(type_id):
    """Render the production cost breakdown for a crafted item."""
    from itertools import groupby
    from sqlalchemy.orm import joinedload
    from sqlalchemy import func
    from evebs.models import Blueprint, BlueprintMaterial, MarketPrice, BpcAsset, UniverseStation, UniverseSystem, MarketOrder
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
    owned_quantities = {}
    current_station = None
    output_buyers = []
    input_sellers = {}

    if blueprint:
        mat_type_ids = [m.universe_type_id for m in blueprint.blueprint_materials]
        market_prices = {
            mp.type_id: mp
            for mp in MarketPrice.query.filter(
                MarketPrice.type_id.in_(mat_type_ids + [type_id])
            ).all()
        }
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

    taxes = Constant.query.filter_by(libe='taxes').first()
    taxes_value = taxes.f_value if taxes else 1.13
    return render_template('production_costs/show.html',
                           item=item,
                           blueprint=blueprint,
                           market_prices=market_prices,
                           owned_quantities=owned_quantities,
                           taxes=taxes_value,
                           current_station=current_station,
                           output_buyers=output_buyers,
                           input_sellers=input_sellers,
                           title=f'Production cost — {item.name}')


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
