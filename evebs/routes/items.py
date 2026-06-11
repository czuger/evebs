from types import SimpleNamespace

from flask import Blueprint, render_template, abort
from flask_login import current_user

from evebs.models import EveItem, UniverseSystem, JitaMinPrice
from evebs.models.tables.buy_orders_analytic import BuyOrdersAnalytic

bp = Blueprint('items', __name__)

_DEFAULT_MFG_TAXES = {'system_cost_index': 5.0, 'scc_tax': 4.0, 'standard_tax': 1.0}
_DEFAULT_RXN_TAXES = {'system_cost_index': 5.0, 'scc_tax': 4.0, 'reaction_tax': 1.0}


def _manufacturing_context(item):
    """Return a SimpleNamespace with full manufacturing/reaction cost details, or None."""
    bp_obj = item.blueprint
    if not bp_obj or not bp_obj.manufacturing_tree:
        return None

    chain    = bp_obj.manufacturing_tree
    mat_ids  = [int(k) for k in chain]
    item_map = {ei.id: ei for ei in EveItem.query.filter(EveItem.id.in_(mat_ids)).all()}
    jma_map  = {jma.id: jma.min_sell_price
                for jma in JitaMinPrice.query.filter(JitaMinPrice.id.in_(mat_ids)).all()}

    materials = []
    for mat_id_str, mat_data in chain.items():
        mat_item = item_map.get(int(mat_id_str))
        if mat_item:
            materials.append(SimpleNamespace(
                required_qtt=mat_data['quantity'],
                eve_item=mat_item,
                jita_price=jma_map.get(int(mat_id_str)),
            ))

    prod_qtt       = bp_obj.prod_qtt or 1
    batch_mat_cost = sum((m.jita_price or 0) * m.required_qtt for m in materials)
    unit_mat_cost  = batch_mat_cost / prod_qtt

    is_reaction = getattr(bp_obj, 'activity_type', 'manufacturing') == 'reaction'
    if current_user.is_authenticated and current_user.industry_taxes:
        it = current_user.industry_taxes
        if is_reaction:
            block = it.get('reaction', _DEFAULT_RXN_TAXES)
            act_tax_key, act_tax_label = 'reaction_tax', 'Reaction tax'
        else:
            block = it.get('manufacturing', _DEFAULT_MFG_TAXES)
            act_tax_key, act_tax_label = 'standard_tax', 'Standard tax'
    else:
        block = _DEFAULT_RXN_TAXES if is_reaction else _DEFAULT_MFG_TAXES
        act_tax_key, act_tax_label = ('reaction_tax', 'Reaction tax') if is_reaction else ('standard_tax', 'Standard tax')

    sci     = block.get('system_cost_index', 5.0)
    scc     = block.get('scc_tax', 4.0)
    act_tax = block.get(act_tax_key, 1.0)

    unit_sci_cost  = unit_mat_cost * sci / 100
    unit_scc_cost  = unit_mat_cost * scc / 100
    unit_act_cost  = unit_mat_cost * act_tax / 100
    unit_tax_total = unit_sci_cost + unit_scc_cost + unit_act_cost
    unit_total     = unit_mat_cost + unit_tax_total

    return SimpleNamespace(
        activity_type=bp_obj.activity_type,
        prod_qtt=prod_qtt,
        nb_runs=bp_obj.nb_runs,
        materials=materials,
        batch_mat_cost=batch_mat_cost,
        unit_mat_cost=unit_mat_cost,
        sci=sci,           unit_sci_cost=unit_sci_cost,
        scc=scc,           unit_scc_cost=unit_scc_cost,
        act_tax=act_tax,   unit_act_cost=unit_act_cost,
        act_tax_label=act_tax_label,
        unit_tax_total=unit_tax_total,
        unit_total=unit_total,
    )


@bp.route('/items/<slug>')
def show(slug):
    item = EveItem.find_by_slug(slug)
    if item is None:
        abort(404)
    jita      = UniverseSystem.query.filter_by(id=30000142, trade_hub=True).first()
    mfg       = _manufacturing_context(item)
    jma_item  = JitaMinPrice.query.get(item.id)
    jita_buy  = BuyOrdersAnalytic.query.filter_by(eve_item_id=item.id, universe_system_id=30000142).first()
    return render_template('items/show.html',
                           item=item,
                           jita=jita,
                           mfg=mfg,
                           jma_item=jma_item,
                           jita_buy=jita_buy,
                           title=item.name)
