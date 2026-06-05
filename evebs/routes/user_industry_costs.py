from types import SimpleNamespace

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import text

from evebs.extensions import db
from evebs.utils import SimplePagination

bp = Blueprint('user_industry_costs', __name__)
PER_PAGE = 50

_SQL = """
    SELECT
        user_id, user_name,
        blueprint_id, produced_type_id, activity_type,
        blueprint_name, item_name, item_slug,
        mat_cost_per_unit,
        ind_tax_per_unit,
        mat_cost_per_unit + ind_tax_per_unit                AS total_cost_per_unit,
        jita_sell_price,
        jita_sell_price - mat_cost_per_unit - ind_tax_per_unit AS margin_per_unit
    FROM user_industry_costs
    WHERE user_id      = :user_id
      AND activity_type = :activity_type
    ORDER BY (jita_sell_price - mat_cost_per_unit - ind_tax_per_unit) DESC
"""


def _show(activity_type):
    page = request.args.get('page', 1, type=int)
    user = current_user

    params = {'user_id': user.id, 'activity_type': activity_type}

    total = db.session.execute(
        text(f'SELECT COUNT(*) FROM ({_SQL}) t'),
        params,
    ).scalar()

    rows_raw = db.session.execute(
        text(_SQL + ' LIMIT :limit OFFSET :offset'),
        {**params, 'limit': PER_PAGE, 'offset': (page - 1) * PER_PAGE},
    ).mappings().all()

    rows = [SimpleNamespace(**r) for r in rows_raw]
    pagination = SimplePagination(page, PER_PAGE, total) if total else None

    return render_template(
        'user_industry_costs/show.html',
        title=f'Industry costs — {activity_type}',
        rows=rows,
        pagination=pagination,
        activity_type=activity_type,
        user=user,
    )


@bp.route('/user_industry_costs/manufacturing')
@login_required
def show_manufacturing():
    return _show('manufacturing')


@bp.route('/user_industry_costs/reaction')
@login_required
def show_reaction():
    return _show('reaction')
