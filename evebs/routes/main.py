from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Redirect authenticated users to their item list; show landing page otherwise."""
    if current_user.is_authenticated:
        return redirect(url_for('list_items.show'))
    return render_template('index.html', title='Eve Online Business Advisor')
