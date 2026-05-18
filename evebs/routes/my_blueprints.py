import math
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from evebs.extensions import db
from evebs.models import BpcAsset, Blueprint as BpModel, MarketPrice

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
            tax_rate = cost_index * (
                1 + current_user.facility_tax / 100 + current_user.scc_surcharge / 100
            )

    rows_raw = (
        db.session.query(BpcAsset, BpModel)
        .join(BpModel, BpcAsset.eve_item_id == BpModel.id)
        .filter(BpcAsset.user_id == current_user.id)
        .options(joinedload(BpModel.blueprint_materials))
        .all()
    )

    type_ids = set()
    for _asset, blueprint in rows_raw:
        type_ids.add(blueprint.produced_type_id)
        for mat in blueprint.blueprint_materials:
            type_ids.add(mat.universe_type_id)

    market_prices = {
        mp.type_id: mp
        for mp in MarketPrice.query.filter(MarketPrice.type_id.in_(type_ids)).all()
    }

    rows = []
    for asset, blueprint in rows_raw:
        fab_cost = sum(
            mat.required_qtt * market_prices[mat.universe_type_id].adjusted_price
            for mat in blueprint.blueprint_materials
            if mat.universe_type_id in market_prices
            and market_prices[mat.universe_type_id].adjusted_price is not None
        )
        tax_amount = fab_cost * tax_rate
        result_mp = market_prices.get(blueprint.produced_type_id)
        result_price = result_mp.adjusted_price if result_mp and result_mp.adjusted_price else None
        benefit = (result_price * blueprint.prod_qtt - fab_cost - tax_amount
                   if result_price is not None else None)
        rows.append({
            'asset': asset,
            'blueprint': blueprint,
            'fab_cost': fab_cost,
            'tax_amount': tax_amount,
            'result_price': result_price,
            'benefit': benefit,
        })

    rows.sort(key=lambda r: r['benefit'] if r['benefit'] is not None else float('-inf'), reverse=True)

    page = request.args.get('page', 1, type=int)
    pagination = _Pagination(rows, page, PER_PAGE)

    return render_template('my_blueprints/show.html',
                           rows=pagination.items,
                           pagination=pagination,
                           tax_rate=tax_rate,
                           cheapest_facility=cheapest_facility,
                           title='My blueprints')
