from flask import Blueprint, render_template, abort, request
from flask_login import current_user

from evebs.extensions import db
from evebs.models import UniverseType, Constant, TradeHub, WeeklyPriceDetail

bp = Blueprint('production_costs', __name__)
PER_PAGE = 20


@bp.route('/production_costs/<int:type_id>')
def show(type_id):
    """Render the production cost breakdown for a crafted item."""
    from sqlalchemy.orm import joinedload
    from sqlalchemy import func
    from evebs.models import Blueprint, MarketPrice, BpcAsset

    item = UniverseType.query.get(type_id)
    if item is None:
        abort(404)

    blueprint = (Blueprint.query
                 .filter_by(produced_type_id=type_id)
                 .options(joinedload(Blueprint.blueprint_materials))
                 .first())

    market_prices = {}
    owned_quantities = {}
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

    taxes = Constant.query.filter_by(libe='taxes').first()
    taxes_value = taxes.f_value if taxes else 1.13
    return render_template('production_costs/show.html',
                           item=item,
                           blueprint=blueprint,
                           market_prices=market_prices,
                           owned_quantities=owned_quantities,
                           taxes=taxes_value,
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
