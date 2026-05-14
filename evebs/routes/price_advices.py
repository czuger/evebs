from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from evebs.models import PriceAdviceMarginComp

bp = Blueprint('price_advices', __name__)
PER_PAGE = 12


def _advice_prices_margins(margin_type):
    page = request.args.get('page', 1, type=int)
    user = current_user

    col = (PriceAdviceMarginComp.margin_comp_immediate
           if margin_type == 'daily'
           else PriceAdviceMarginComp.margin_comp_weekly)

    q = PriceAdviceMarginComp.query.filter(
        PriceAdviceMarginComp.user_id == user.id,
        col.isnot(None),
    )

    if user.min_amount_for_advice:
        q = q.filter(col > user.min_amount_for_advice)
    if user.min_pcent_for_advice:
        q = q.filter(PriceAdviceMarginComp.margin_percent * 100 > user.min_pcent_for_advice)

    q = q.order_by(col.desc())
    pagination = q.paginate(page=page, per_page=PER_PAGE)
    return pagination, user, margin_type


@bp.route('/price_advices/advice_prices_weekly')
@login_required
def advice_prices_weekly():
    pagination, user, margin_type = _advice_prices_margins('weekly')
    return render_template('price_advices/advice_prices_weekly.html',
                           title='Show rentability with sell orders - weekly average',
                           items=pagination.items,
                           pagination=pagination,
                           user=user,
                           margin_type=margin_type)


@bp.route('/price_advices/advice_prices')
@login_required
def advice_prices():
    pagination, user, margin_type = _advice_prices_margins('daily')
    return render_template('price_advices/advice_prices.html',
                           title='Show rentability with sell orders - immediate price',
                           items=pagination.items,
                           pagination=pagination,
                           user=user,
                           margin_type=margin_type)


@bp.route('/price_advices/empty_places')
@login_required
def empty_places():
    from evebs.models import PriceAdvicesMinPrice
    page = request.args.get('page', 1, type=int)
    q = PriceAdvicesMinPrice.query.filter(
        PriceAdvicesMinPrice.min_price.is_(None),
        PriceAdvicesMinPrice.vol_month.isnot(None),
    ).order_by(PriceAdvicesMinPrice.vol_month.desc())
    pagination = q.paginate(page=page, per_page=PER_PAGE)
    return render_template('price_advices/empty_places.html',
                           items=pagination.items,
                           pagination=pagination)
