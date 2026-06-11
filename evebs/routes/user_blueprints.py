from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from config import PER_PAGE
from evebs.models import UserBlueprintExtended
from evebs.utils import SimplePagination

bp = Blueprint('user_blueprints', __name__)


@bp.route('/user_blueprints')
@login_required
def show():
    page       = request.args.get('page', 1, type=int)
    group_name = request.args.get('group', '')

    base_q = (
        UserBlueprintExtended.query
        .filter_by(user_id=current_user.id)
        .order_by(UserBlueprintExtended.item_name)
    )

    groups = sorted(
        r[0] for r in
        UserBlueprintExtended.query
        .filter_by(user_id=current_user.id)
        .with_entities(UserBlueprintExtended.market_group_name)
        .distinct()
        if r[0]
    )

    if group_name:
        base_q = base_q.filter(UserBlueprintExtended.market_group_name == group_name)

    total      = base_q.count()
    blueprints = base_q.limit(PER_PAGE).offset((page - 1) * PER_PAGE).all()
    pagination = SimplePagination(page, PER_PAGE, total)

    return render_template('user_blueprints/show.html',
                           blueprints=blueprints,
                           total=total,
                           pagination=pagination,
                           groups=groups,
                           selected_group=group_name)
