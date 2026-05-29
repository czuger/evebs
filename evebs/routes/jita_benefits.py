from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy.orm import joinedload

from evebs.models import JitaManufacturingMargins, EveItem

bp = Blueprint('jita_benefits', __name__)
PER_PAGE = 50


@bp.route('/jita_benefits')
@login_required
def show():
    page = request.args.get('page', 1, type=int)

    q = (
        JitaManufacturingMargins.query
        .options(joinedload(JitaManufacturingMargins.eve_item).joinedload(EveItem.market_group))
        .filter(JitaManufacturingMargins.benefit.isnot(None))
        .order_by(JitaManufacturingMargins.benefit.desc())
    )

    pagination = q.paginate(page=page, per_page=PER_PAGE)
    return render_template(
        'jita_benefits/show.html',
        rows=pagination.items,
        pagination=pagination,
    )
