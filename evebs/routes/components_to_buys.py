from flask import Blueprint, render_template
from flask_login import login_required, current_user

from evebs.models import ComponentToBuy

bp = Blueprint('components_to_buys', __name__)


@bp.route('/components_to_buys')
@login_required
def show():
    user = current_user
    components = ComponentToBuy.query.filter_by(user_id=user.id).all()
    return render_template('components_to_buys/show.html',
                           title='Components to buy',
                           components=components,
                           user=user)
