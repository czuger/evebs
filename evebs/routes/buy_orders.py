from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from evebs.models import BuyOrdersAnalyticsResult

bp = Blueprint('buy_orders', __name__)
PER_PAGE = 12


@bp.route('/buy_orders')
@login_required
def show():
    page = request.args.get('page', 1, type=int)
    user = current_user

    if user.batch_cap:
        q = BuyOrdersAnalyticsResult.query.filter(
            BuyOrdersAnalyticsResult.user_id == user.id,
            BuyOrdersAnalyticsResult.capped_margin > 0,
        ).order_by(BuyOrdersAnalyticsResult.capped_margin.desc())
    else:
        q = BuyOrdersAnalyticsResult.query.filter(
            BuyOrdersAnalyticsResult.user_id == user.id,
            BuyOrdersAnalyticsResult.full_margin > 0,
        ).order_by(BuyOrdersAnalyticsResult.full_margin.desc())

    pagination = q.paginate(page=page, per_page=PER_PAGE)
    owned_bp_ids = {b.produced_type_id for b in user.blueprints}
    return render_template('buy_orders/show.html',
                           title='Show rentability with buy orders',
                           buy_orders=pagination.items,
                           pagination=pagination,
                           owned_bp_ids=owned_bp_ids,
                           user=user)
