from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from evebs.extensions import db
from evebs.models import UserSaleOrderDetail, User

bp = Blueprint('user_sales_orders', __name__)
PER_PAGE = 20


@bp.route('/user_sales_orders')
@login_required
def show():
    """Render the user's active sell orders filtered by minimum margin."""
    user = current_user
    margin_min = user.sales_orders_show_margin_min
    q = UserSaleOrderDetail.query.filter_by(user_id=user.id)
    if margin_min:
        q = q.filter(UserSaleOrderDetail.min_price_margin_pcent * 100 >= margin_min)
    orders = q.order_by(UserSaleOrderDetail.price_delta.desc()).all()
    return render_template('user_sales_orders/show.html',
                           title='My sales orders',
                           orders=orders,
                           user=user)


@bp.route('/user_sales_orders/update', methods=['POST'])
@login_required
def update():
    """Save the user's minimum margin preference for the sales order view."""
    user = current_user
    margin_min = request.form.get('sales_orders_show_margin_min', type=int)
    user.sales_orders_show_margin_min = margin_min
    db.session.commit()
    return redirect(url_for('user_sales_orders.show'))
