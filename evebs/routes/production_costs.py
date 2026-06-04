from types import SimpleNamespace

from flask import Blueprint, render_template, abort
from flask_login import current_user

from evebs.models import EveItem, JitaMarketAnalytics, Constant

bp = Blueprint('production_costs', __name__)


def _build_materials(item: EveItem) -> list:
    """Return direct materials for item's blueprint from Blueprint.manufacturing_tree."""
    if not item.blueprint_id or not item.blueprint:
        return []
    chain = item.blueprint.manufacturing_tree
    if not chain:
        return []
    mat_ids = [int(k) for k in chain]
    item_map = {ei.id: ei for ei in EveItem.query.filter(EveItem.id.in_(mat_ids)).all()}
    jma_map = {jma.id: jma.min_sell_price
               for jma in JitaMarketAnalytics.query.filter(JitaMarketAnalytics.id.in_(mat_ids)).all()}
    materials = []
    for mat_id_str, mat_data in chain.items():
        mat_item = item_map.get(int(mat_id_str))
        if mat_item:
            materials.append(SimpleNamespace(
                required_qtt=mat_data['quantity'],
                eve_item=mat_item,
                jita_price=jma_map.get(int(mat_id_str)),
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
