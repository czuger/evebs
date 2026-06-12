from types import SimpleNamespace

from flask import Blueprint as FlaskBlueprint, render_template, request
from flask_login import login_required
from sqlalchemy import text

from config import PER_PAGE
from evebs.extensions import db
from evebs.utils import SimplePagination

bp = FlaskBlueprint('jita_min_prices', __name__)

_SELECT = """
    SELECT
        ei.id AS item_id, ei.name AS item_name, ei.slug AS item_slug,
        COALESCE(mg.name, '') AS market_group_name,
        jma.min_sell_price, jma.updated_at
    FROM jita_min_prices jma
    JOIN eve_items ei ON ei.id = jma.id
    LEFT JOIN market_groups mg ON mg.id = ei.market_group_id
"""

_ORDER = """
    ORDER BY jma.min_sell_price DESC NULLS LAST, ei.name ASC
"""


@bp.route('/jita_min_prices')
@login_required
def show():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str).strip()

    where = ''
    params = {}
    if q:
        where = ' WHERE LOWER(ei.name) LIKE :q'
        params['q'] = f'%{q.lower()}%'

    total = db.session.execute(
        text(f'SELECT COUNT(*) FROM ({_SELECT + where}) t'),
        params,
    ).scalar()

    rows_raw = db.session.execute(
        text(_SELECT + where + _ORDER + ' LIMIT :limit OFFSET :offset'),
        {**params, 'limit': PER_PAGE, 'offset': (page - 1) * PER_PAGE},
    ).mappings().all()

    rows = [SimpleNamespace(**r) for r in rows_raw]
    pagination = SimplePagination(page, PER_PAGE, total) if total else None

    return render_template(
        'jita_min_prices/show.html',
        rows=rows,
        pagination=pagination,
        q=q,
    )
