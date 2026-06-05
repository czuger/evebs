from types import SimpleNamespace

from flask import Blueprint, render_template, abort
from flask_login import current_user

from evebs.models import EveItem, JitaMarketAnalytics

bp = Blueprint('production_costs', __name__)

_DEFAULT_MFG_TAXES = {'system_cost_index': 5.0, 'scc_tax': 4.0, 'standard_tax': 1.0}
_DEFAULT_RXN_TAXES = {'system_cost_index': 5.0, 'scc_tax': 4.0, 'reaction_tax': 1.0}


def _get_tax_block(item):
    """Return the tax dict for this item's activity type.

    Falls back to hardcoded defaults when the user is not authenticated or
    has no industry_taxes configured.
    """
    bp_obj = item.blueprint
    if bp_obj is None:
        return _DEFAULT_MFG_TAXES, 'standard_tax', 'Standard tax'

    is_reaction = getattr(bp_obj, 'activity_type', 'manufacturing') == 'reaction'

    if current_user.is_authenticated and current_user.industry_taxes:
        it = current_user.industry_taxes
        if is_reaction:
            block = it.get('reaction', _DEFAULT_RXN_TAXES)
            return block, 'reaction_tax', 'Reaction tax'
        else:
            block = it.get('manufacturing', _DEFAULT_MFG_TAXES)
            return block, 'standard_tax', 'Standard tax'

    if is_reaction:
        return _DEFAULT_RXN_TAXES, 'reaction_tax', 'Reaction tax'
    return _DEFAULT_MFG_TAXES, 'standard_tax', 'Standard tax'


def _build_materials(item):
    """Return direct materials with Jita prices from Blueprint.manufacturing_tree."""
    if not item.blueprint_id or not item.blueprint:
        return []
    chain = item.blueprint.manufacturing_tree
    if not chain:
        return []
    mat_ids = [int(k) for k in chain]
    item_map = {ei.id: ei for ei in EveItem.query.filter(EveItem.id.in_(mat_ids)).all()}
    jma_map  = {jma.id: jma.min_sell_price
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

    materials   = _build_materials(item)
    bp_obj      = item.blueprint
    prod_qtt    = bp_obj.prod_qtt if bp_obj and bp_obj.prod_qtt else 1

    batch_mat_cost = sum(
        (m.jita_price or 0) * m.required_qtt for m in materials
    )
    unit_mat_cost = batch_mat_cost / prod_qtt

    tax_block, act_tax_key, act_tax_label = _get_tax_block(item)
    sci      = tax_block.get('system_cost_index', 5.0)
    scc      = tax_block.get('scc_tax', 4.0)
    act_tax  = tax_block.get(act_tax_key, 1.0)

    unit_sci_cost = unit_mat_cost * sci / 100
    unit_scc_cost = unit_mat_cost * scc / 100
    unit_act_cost = unit_mat_cost * act_tax / 100
    unit_tax_total = unit_sci_cost + unit_scc_cost + unit_act_cost
    unit_total     = unit_mat_cost + unit_tax_total

    return render_template(
        'production_costs/show.html',
        item=item,
        materials=materials,
        prod_qtt=prod_qtt,
        batch_mat_cost=batch_mat_cost,
        unit_mat_cost=unit_mat_cost,
        sci=sci,           unit_sci_cost=unit_sci_cost,
        scc=scc,           unit_scc_cost=unit_scc_cost,
        act_tax=act_tax,   unit_act_cost=unit_act_cost,
        act_tax_label=act_tax_label,
        unit_tax_total=unit_tax_total,
        unit_total=unit_total,
        title=f'Production cost — {item.name}',
    )
