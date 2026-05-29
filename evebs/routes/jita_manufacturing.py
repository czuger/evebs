from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from evebs.models import JitaManufacturingMargins, EveItem
from evebs.models import Blueprint as BlueprintModel

bp = Blueprint('jita_manufacturing', __name__)
PER_PAGE = 20


@bp.route('/jita_manufacturing')
@login_required
def show():
    page = request.args.get('page', 1, type=int)

    user_bp_ids = [b.id for b in current_user.blueprints]

    q = (
        JitaManufacturingMargins.query
        .options(joinedload(JitaManufacturingMargins.eve_item).joinedload(EveItem.market_group))
        .join(EveItem, EveItem.id == JitaManufacturingMargins.eve_item_id)
        .join(BlueprintModel, BlueprintModel.id == EveItem.blueprint_id)
        .filter(BlueprintModel.id.in_(user_bp_ids))
        .filter(JitaManufacturingMargins.benefit.isnot(None))
        .order_by(JitaManufacturingMargins.benefit.desc())
    )

    pagination = q.paginate(page=page, per_page=PER_PAGE)
    return render_template(
        'jita_manufacturing/show.html',
        rows=pagination.items,
        pagination=pagination,
    )
