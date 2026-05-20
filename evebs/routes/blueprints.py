from flask import Blueprint, render_template, request
from evebs.models import Blueprint as BpModel, BlueprintCost, UniverseType, UniverseGroup, UniverseCategory
from evebs.routes.my_blueprints import _Pagination
from evebs.extensions import db

bp = Blueprint('blueprints', __name__)
PER_PAGE = 20


@bp.route('/blueprints')
def show():
    category_id = request.args.get('category_id', type=int)
    group_id = request.args.get('group_id', type=int)

    # Categories that have at least one blueprint with cost data
    categories = (
        db.session.query(UniverseCategory.id, UniverseCategory.name)
        .join(UniverseGroup, UniverseGroup.category_id == UniverseCategory.id)
        .join(UniverseType, UniverseType.group_id == UniverseGroup.id)
        .join(BpModel, BpModel.produced_type_id == UniverseType.id)
        .distinct()
        .order_by(UniverseCategory.name)
        .all()
    )

    # Groups for the selected category
    groups = []
    if category_id:
        groups = (
            db.session.query(UniverseGroup.id, UniverseGroup.name)
            .join(UniverseType, UniverseType.group_id == UniverseGroup.id)
            .join(BpModel, BpModel.produced_type_id == UniverseType.id)
            .filter(UniverseGroup.category_id == category_id)
            .distinct()
            .order_by(UniverseGroup.name)
            .all()
        )

    query = (
        BpModel.query
        .join(BlueprintCost,
              (BpModel.produced_type_id == BlueprintCost.produced_type_id) &
              (BlueprintCost.system_id == 30000142))
        .add_entity(BlueprintCost)
    )
    if group_id:
        query = (query
                 .join(UniverseType, BpModel.produced_type_id == UniverseType.id)
                 .filter(UniverseType.group_id == group_id))
    elif category_id:
        query = (query
                 .join(UniverseType, BpModel.produced_type_id == UniverseType.id)
                 .join(UniverseGroup, UniverseType.group_id == UniverseGroup.id)
                 .filter(UniverseGroup.category_id == category_id))

    rows_raw = query.all()

    rows = []
    for blueprint, bc in rows_raw:
        benefit = (
            (bc.batch_revenue_buy - bc.material_cost_sell)
            if bc.batch_revenue_buy is not None and bc.material_cost_sell is not None
            else None
        )
        rows.append({'blueprint': blueprint, 'bc': bc, 'benefit': benefit})

    _SORT_KEYS = {
        'name':          lambda r: r['blueprint'].name or '',
        'cost':          lambda r: r['bc'].material_cost_sell,
        'revenue':       lambda r: r['bc'].batch_revenue_buy,
        'benefit':       lambda r: r['benefit'],
        'craft_vs_sell': lambda r: r['bc'].craft_vs_sell_margin,
    }
    sort_col = request.args.get('sort', 'benefit')
    sort_dir = request.args.get('dir', 'desc')
    if sort_col not in _SORT_KEYS:
        sort_col = 'benefit'
    key_fn = _SORT_KEYS[sort_col]
    reverse = sort_dir != 'asc'
    rows.sort(
        key=lambda r: (key_fn(r) is None, key_fn(r) if key_fn(r) is not None else 0),
        reverse=reverse,
    )

    page = request.args.get('page', 1, type=int)
    pagination = _Pagination(rows, page, PER_PAGE)

    return render_template('blueprints/show.html',
                           rows=pagination.items,
                           pagination=pagination,
                           sort_col=sort_col,
                           sort_dir=sort_dir,
                           categories=categories,
                           groups=groups,
                           category_id=category_id,
                           group_id=group_id,
                           title='All blueprints')
