from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace

from flask import Blueprint as FlaskBlueprint, render_template, request, abort
from flask_login import current_user, login_required
from sqlalchemy import func

from config import PER_PAGE
from evebs.extensions import db
from evebs.models import (EveItem, UniverseSystem, JitaMinPrice, MarketHistory, PublicTradeOrder,
                          UserAsset, LastViewedItem)
from evebs.models.tables.associations import user_blueprints
from evebs.models.tables.blueprint import Blueprint as BlueprintModel
from evebs.utils import SimplePagination

bp = FlaskBlueprint('items', __name__)

FORGE_REGION_ID = 10000002
JITA_SYSTEM_ID = 30000142
MAX_RECIPROCAL = 40


def _bp_display_name(bp_obj):
    """A blueprint's market name (e.g. 'Gram II Blueprint') from its Blueprint row."""
    n = (bp_obj.name if bp_obj else '') or ''
    return n if n.lower().endswith('blueprint') else f'{n} Blueprint'

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


def _record_view(item):
    """Upsert the current user's view of `item`, bumping its view_count on each visit."""
    row = LastViewedItem.query.filter_by(user_id=current_user.id, eve_item_id=item.id).first()
    if row:
        row.view_count += 1
        row.viewed_at = datetime.now(UTC)
    else:
        db.session.add(LastViewedItem(user_id=current_user.id, eve_item_id=item.id))
    db.session.commit()


@bp.route('/items/search')
@login_required
def search():
    q = request.args.get('q', '', type=str).strip()
    page = request.args.get('page', 1, type=int)
    items, pagination = [], None
    if q:
        pattern = f"%{q.lower().replace(' ', '%')}%"
        query = EveItem.query.filter(func.lower(EveItem.name).like(pattern)).order_by(EveItem.name)
        total = query.count()
        items = query.limit(PER_PAGE).offset((page - 1) * PER_PAGE).all()
        pagination = SimplePagination(page, PER_PAGE, total) if total else None
    return render_template('items/search.html', items=items, q=q, pagination=pagination)


@bp.route('/items/last_viewed')
@login_required
def last_viewed():
    page = request.args.get('page', 1, type=int)
    query = (LastViewedItem.query.filter_by(user_id=current_user.id)
             .order_by(LastViewedItem.view_count.desc(), LastViewedItem.viewed_at.desc()))
    total = query.count()
    rows = query.limit(PER_PAGE).offset((page - 1) * PER_PAGE).all()
    pagination = SimplePagination(page, PER_PAGE, total) if total else None
    return render_template('items/last_viewed.html', rows=rows, pagination=pagination)


@bp.route('/items/<slug>')
def show(slug):
    item = EveItem.find_by_slug(slug)
    if item is None:
        abort(404)
    if current_user.is_authenticated:
        _record_view(item)
    jita      = UniverseSystem.query.filter_by(id=JITA_SYSTEM_ID, trade_hub=True).first()
    mfg       = _manufacturing_context(item)
    jma_item  = JitaMinPrice.query.get(item.id)

    # Market price summary (None → shown as "—"). Jita min sell is the P10 ask analytic; the
    # other three are live min sell / max buy straight from public_trade_orders.
    jita_min_sell = jma_item.min_sell_price if jma_item else None
    jita_max_buy  = (PublicTradeOrder.query
                     .filter_by(eve_item_id=item.id, is_buy_order=True, universe_system_id=JITA_SYSTEM_ID)
                     .with_entities(func.max(PublicTradeOrder.price)).scalar())
    universe_min_sell = (PublicTradeOrder.query
                         .filter_by(eve_item_id=item.id, is_buy_order=False)
                         .with_entities(func.min(PublicTradeOrder.price)).scalar())
    universe_max_buy  = (PublicTradeOrder.query
                         .filter_by(eve_item_id=item.id, is_buy_order=True)
                         .with_entities(func.max(PublicTradeOrder.price)).scalar())

    # "Produced by" — the blueprint that makes this item (when it is a product).
    bp_item = bp_name = None
    # "Invented by" — when this item IS a T2 blueprint that was invented from a T1 one.
    invented = None
    if item.blueprint:
        bp_item = EveItem.query.get(item.blueprint.id)   # the "X Blueprint" market item
        bp_name = bp_item.name if bp_item else _bp_display_name(item.blueprint)
    else:
        this_bp = BlueprintModel.query.get(item.id)      # is this item itself a blueprint?
        if this_bp and this_bp.is_invented_from_id:
            src_item = EveItem.query.get(this_bp.is_invented_from_id)
            src_name = (src_item.name if src_item
                        else _bp_display_name(BlueprintModel.query.get(this_bp.is_invented_from_id)))
            invented = SimpleNamespace(
                id=this_bp.is_invented_from_id,
                name=src_name,
                slug=src_item.slug if src_item else None,
            )

    # "is involved in production of" — products whose recipe uses this item as a direct
    # material (reciprocal of "Produced by"). Top-level keys of manufacturing_tree are the
    # direct materials, so a row matches when str(item.id) is one of them.
    prod_bps = (BlueprintModel.query
                .filter(BlueprintModel.manufacturing_tree[str(item.id)].isnot(None))
                .all())
    prod_ids   = [b.produced_type_id for b in prod_bps]
    prod_items = {ei.id: ei for ei in EveItem.query.filter(EveItem.id.in_(prod_ids)).all()}
    produces = sorted(
        (SimpleNamespace(id=ei.id, name=ei.name, slug=ei.slug)
         for pid in prod_ids if (ei := prod_items.get(pid))),
        key=lambda p: p.name,
    )
    produces_more = max(0, len(produces) - MAX_RECIPROCAL)
    produces = produces[:MAX_RECIPROCAL]

    # "is involved in invention of" — T2 blueprints invented from this item (reciprocal of
    # "Invented by"). Non-empty only when this item is itself a T1 blueprint.
    inv_bps  = BlueprintModel.query.filter_by(is_invented_from_id=item.id).all()
    inv_items = {ei.id: ei
                 for ei in EveItem.query.filter(EveItem.id.in_([b.id for b in inv_bps])).all()}
    invents = sorted(
        (SimpleNamespace(
            id=b.id,
            name=(ei.name if (ei := inv_items.get(b.id)) else _bp_display_name(b)),
            slug=(ei.slug if (ei := inv_items.get(b.id)) else None),
         ) for b in inv_bps),
        key=lambda v: v.name,
    )

    # User-specific ownership indicators (only meaningful when logged in).
    has_asset = has_blueprint = has_inv_blueprint = False
    if current_user.is_authenticated:
        has_asset = db.session.query(UserAsset.id).filter_by(
            user_id=current_user.id, eve_item_id=item.id).first() is not None
        if item.blueprint_id:
            has_blueprint = db.session.query(user_blueprints.c.id).filter_by(
                user_id=current_user.id, blueprint_id=item.blueprint_id).first() is not None
        if item.blueprint and item.blueprint.is_invented_from_id:
            has_inv_blueprint = db.session.query(user_blueprints.c.id).filter_by(
                user_id=current_user.id,
                blueprint_id=item.blueprint.is_invented_from_id).first() is not None

    cutoff = date.today() - timedelta(days=365)
    hist_rows = (MarketHistory.query
                 .filter(MarketHistory.region_id == FORGE_REGION_ID,
                         MarketHistory.type_id == item.id,
                         MarketHistory.date >= cutoff)
                 .order_by(MarketHistory.date).all())
    history = [{'date': h.date.isoformat(), 'average': h.average, 'volume': h.volume}
               for h in hist_rows]

    return render_template('items/show.html',
                           item=item,
                           jita=jita,
                           mfg=mfg,
                           jita_min_sell=jita_min_sell,
                           jita_max_buy=jita_max_buy,
                           universe_min_sell=universe_min_sell,
                           universe_max_buy=universe_max_buy,
                           bp_item=bp_item,
                           bp_name=bp_name,
                           invented=invented,
                           produces=produces,
                           produces_more=produces_more,
                           invents=invents,
                           has_asset=has_asset,
                           has_blueprint=has_blueprint,
                           has_inv_blueprint=has_inv_blueprint,
                           history=history,
                           title=item.name)
