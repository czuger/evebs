from types import SimpleNamespace

from flask import Blueprint, render_template, abort, request
from flask_login import current_user

from evebs.models import EveItem, Constant, WeeklyPriceDetail

bp = Blueprint('production_costs', __name__)
PER_PAGE = 20


def _build_materials(item: EveItem) -> list:
    """Return direct materials for item's blueprint from Blueprint.manufacturing_tree."""
    if not item.blueprint_id or not item.blueprint:
        return []
    chain = item.blueprint.manufacturing_tree
    if not chain:
        return []
    mat_ids = [int(k) for k in chain]
    item_map = {ei.id: ei for ei in EveItem.query.filter(EveItem.id.in_(mat_ids)).all()}
    materials = []
    for mat_id_str, mat_data in chain.items():
        mat_item = item_map.get(int(mat_id_str))
        if mat_item:
            materials.append(SimpleNamespace(
                required_qtt=mat_data['quantity'],
                eve_item=mat_item,
            ))
    return materials


@bp.route('/production_costs/<slug>')
def show(slug):
    item = EveItem.find_by_slug(slug)
    if item is None:
        abort(404)
    if item.base_item:
        abort(400)
    taxes = Constant.query.filter_by(libe='taxes').first()
    taxes_value = taxes.f_value if taxes else 1.13
    materials = _build_materials(item)
    return render_template('production_costs/show.html',
                           item=item,
                           materials=materials,
                           taxes=taxes_value,
                           title=f'Production cost estimation for {item.name}')


@bp.route('/production_costs/<item_slug>/dailies_avg_prices/<int:trade_hub_id>')
def dailies_avg_prices(item_slug, trade_hub_id):
    item = EveItem.find_by_slug(item_slug)
    if item is None:
        abort(404)
    if not item.base_item:
        abort(400)
    page = request.args.get('page', 1, type=int)
    q = WeeklyPriceDetail.query.filter_by(
        eve_item_id=item.id,
        universe_system_id=trade_hub_id,
    ).order_by(WeeklyPriceDetail.day.desc())
    pagination = q.paginate(page=page, per_page=PER_PAGE)
    return render_template('production_costs/dailies_avg_prices.html',
                           item=item,
                           dailies_details=pagination.items,
                           pagination=pagination,
                           title=f'Weekly average price detail for {item.name}')


@bp.route('/production_costs/<slug>/market_histories')
def market_histories(slug):
    from evebs.models import EveMarketHistoriesGroup
    item = EveItem.find_by_slug(slug)
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
