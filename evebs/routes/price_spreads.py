from flask import Blueprint, render_template, request
from flask_login import login_required

from config import PER_PAGE
from evebs.models import JitaPriceSpread
from evebs.utils import SimplePagination

bp = Blueprint('price_spreads', __name__)


@bp.route('/price_spreads')
@login_required
def show():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str).strip()

    query = JitaPriceSpread.query
    if q:
        query = query.filter(JitaPriceSpread.item_name.ilike(f'%{q}%'))

    total = query.count()
    rows = (query.order_by(JitaPriceSpread.spread_pcent.desc().nullslast(),
                           JitaPriceSpread.item_name)
            .limit(PER_PAGE)
            .offset((page - 1) * PER_PAGE)
            .all())

    pagination = SimplePagination(page, PER_PAGE, total) if total else None

    return render_template('price_spreads/show.html', rows=rows, pagination=pagination, q=q)
