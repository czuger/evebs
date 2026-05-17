from flask import Blueprint, render_template, abort, request
from flask_login import current_user

from evebs.models import UniverseType, Constant, TradeHub, WeeklyPriceDetail

bp = Blueprint('production_costs', __name__)
PER_PAGE = 20


@bp.route('/production_costs/<slug>')
def show(slug):
    item = UniverseType.find_by_slug(slug)
    if item is None:
        abort(404)
    if item.base_item:
        abort(400)
    taxes = Constant.query.filter_by(libe='taxes').first()
    taxes_value = taxes.f_value if taxes else 1.13
    return render_template('production_costs/show.html',
                           item=item,
                           taxes=taxes_value,
                           title=f'Production cost estimation for {item.name}')


@bp.route('/production_costs/<item_slug>/dailies_avg_prices/<int:trade_hub_id>')
def dailies_avg_prices(item_slug, trade_hub_id):
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


@bp.route('/production_costs/<slug>/market_histories')
def market_histories(slug):
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
