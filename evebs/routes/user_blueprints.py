from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint('user_blueprints', __name__)


@bp.route('/user_blueprints')
@login_required
def show():
    return render_template('user_blueprints/show.html',
                           blueprints=current_user.blueprints)


@bp.route('/user_blueprints/refresh', methods=['POST'])
@login_required
def refresh():
    from esi.download_my_blueprints import download_my_blueprints
    download_my_blueprints(current_user)
    return redirect(url_for('user_blueprints.show'))
