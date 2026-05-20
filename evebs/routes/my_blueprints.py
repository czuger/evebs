import math
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from evebs.extensions import db
from evebs.models import BpcAsset, Blueprint as BpModel, BlueprintCost

bp = Blueprint('my_blueprints', __name__)
PER_PAGE = 20


class _Pagination:
    """Minimal pagination wrapper for in-memory lists, compatible with shared/pagination.html."""

    def __init__(self, items_all, page, per_page):
        self.per_page = per_page
        self.total = len(items_all)
        self.pages = math.ceil(self.total / per_page) if per_page else 0
        self.page = max(1, min(page, self.pages or 1))
        start = (self.page - 1) * per_page
        self.items = items_all[start:start + per_page]
        self.has_prev = self.page > 1
        self.has_next = self.page < self.pages
        self.prev_num = self.page - 1
        self.next_num = self.page + 1

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if (num <= left_edge
                    or self.page - left_current - 1 < num < self.page + right_current
                    or num > self.pages - right_edge):
                if last + 1 != num:
                    yield None
                yield num
                last = num


@bp.route('/my_blueprints')
@login_required
def show():
    """Rank owned blueprints by benefit (adjusted result price minus fabrication cost)."""
    from evebs.engine.industry import get_industry_facilities_near

    # Resolve tax rate from cheapest nearby facility
    tax_rate = 0.0
    cheapest_facility = None
    loc = current_user.user_location_station
    if loc and loc.universe_system:
        facilities = get_industry_facilities_near(
            loc.universe_system.name,
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

    rows_raw = (
        db.session.query(BpcAsset, BpModel)
        .join(BpModel, BpcAsset.eve_item_id == BpModel.id)
        .filter(BpcAsset.user_id == current_user.id)
        .all()
    )

    produced_type_ids = [bp.produced_type_id for _, bp in rows_raw]
    bc_by_produced = {
        bc.produced_type_id: bc
        for bc in BlueprintCost.query.filter(
            BlueprintCost.produced_type_id.in_(produced_type_ids),
            BlueprintCost.system_id == 30000142,
        ).all()
    }

    rows = []
    for asset, blueprint in rows_raw:
        bc = bc_by_produced.get(blueprint.produced_type_id)
        batch_cost = bc.material_cost_sell if bc and bc.material_cost_sell is not None else None
        tax_amount = (batch_cost * tax_rate) if batch_cost is not None else None
        batch_revenue = bc.batch_revenue_buy if bc and bc.batch_revenue_buy is not None else None
        benefit = (batch_revenue - batch_cost - (tax_amount or 0)
                   if batch_revenue is not None and batch_cost is not None else None)
        rows.append({
            'asset': asset,
            'blueprint': blueprint,
            'bc': bc,
            'tax_amount': tax_amount,
            'benefit': benefit,
        })

    _SORT_KEYS = {
        'name':          lambda r: r['blueprint'].name or '',
        'qty':           lambda r: r['asset'].quantity or 0,
        'cost':          lambda r: (r['bc'].material_cost_sell  if r['bc'] else None),
        'tax':           lambda r: r['tax_amount'],
        'revenue':       lambda r: (r['bc'].batch_revenue_buy   if r['bc'] else None),
        'benefit':       lambda r: r['benefit'],
        'craft_vs_sell': lambda r: (r['bc'].craft_vs_sell_margin if r['bc'] else None),
    }
    sort_col = request.args.get('sort', 'benefit')
    sort_dir = request.args.get('dir', 'desc')
    if sort_col not in _SORT_KEYS:
        sort_col = 'benefit'
    key_fn = _SORT_KEYS[sort_col]
    reverse = sort_dir != 'asc'
    rows.sort(key=lambda r: (key_fn(r) is None, key_fn(r) if key_fn(r) is not None else 0),
              reverse=reverse)

    page = request.args.get('page', 1, type=int)
    pagination = _Pagination(rows, page, PER_PAGE)

    return render_template('my_blueprints/show.html',
                           rows=pagination.items,
                           pagination=pagination,
                           tax_rate=tax_rate,
                           cheapest_facility=cheapest_facility,
                           sort_col=sort_col,
                           sort_dir=sort_dir,
                           title='My blueprints')
