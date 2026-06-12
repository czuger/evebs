from flask import Blueprint as FlaskBlueprint, render_template, redirect, url_for
from flask_login import current_user

bp = FlaskBlueprint('main', __name__)


@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('buy_orders.show'))
    return render_template('index.html', title='Eve Online Business Advisor')
