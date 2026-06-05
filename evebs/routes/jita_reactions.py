from types import SimpleNamespace

from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import text, bindparam

from config import PER_PAGE
from evebs.extensions import db
from evebs.utils import SimplePagination

bp = Blueprint('jita_reactions', __name__)

_SQL = """
    SELECT
        ei.id AS item_id, ei.name AS item_name, ei.slug AS item_slug,
        COALESCE(mg.name, '') AS market_group_name,
        b.manufacturing_cost AS reaction_cost,
        b.prod_qtt * jma.min_sell_price AS estimated_selling_price,
        b.prod_qtt * jma.min_sell_price * 0.05 AS selling_tax,
        (b.prod_qtt * jma.min_sell_price)
            - (b.prod_qtt * jma.min_sell_price * 0.05)
            - b.manufacturing_cost AS benefit
    FROM blueprints b
    JOIN eve_items ei ON ei.id = b.produced_type_id
    LEFT JOIN market_groups mg ON mg.id = ei.market_group_id
    JOIN jita_market_analytics jma ON jma.id = b.produced_type_id
    WHERE b.activity_type = 'reaction'
      AND b.manufacturing_cost IS NOT NULL
      AND jma.min_sell_price IS NOT NULL
      AND b.id IN :user_bp_ids
    ORDER BY benefit DESC
"""


@bp.route('/jita_reactions')
@login_required
def show():
    page = request.args.get('page', 1, type=int)
    user_bp_ids = [b.id for b in current_user.blueprints]

    if not user_bp_ids:
        return render_template('jita_reactions/show.html', rows=[], pagination=None)

    total = db.session.execute(
        text(f'SELECT COUNT(*) FROM ({_SQL}) t').bindparams(
            bindparam('user_bp_ids', expanding=True)
        ),
        {'user_bp_ids': user_bp_ids},
    ).scalar()

    rows_raw = db.session.execute(
        text(_SQL + ' LIMIT :limit OFFSET :offset').bindparams(
            bindparam('user_bp_ids', expanding=True)
        ),
        {'user_bp_ids': user_bp_ids, 'limit': PER_PAGE, 'offset': (page - 1) * PER_PAGE},
    ).mappings().all()

    rows = [SimpleNamespace(**r) for r in rows_raw]
    pagination = SimplePagination(page, PER_PAGE, total)

    return render_template('jita_reactions/show.html', rows=rows, pagination=pagination)


@bp.route('/jita_reactions/refresh', methods=['POST'])
@login_required
def refresh():
    from esi.download_my_blueprints import download_my_blueprints
    download_my_blueprints(current_user)
    return redirect(url_for('jita_reactions.show'))
