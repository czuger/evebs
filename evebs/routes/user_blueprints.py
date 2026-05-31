from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

from evebs.extensions import db
from evebs.models import Blueprint as BpModel

bp = Blueprint('user_blueprints', __name__)

PER_PAGE = 20


@bp.route('/user_blueprints')
@login_required
def show():
    page = request.args.get('page', 1, type=int)
    pagination = (
        db.session.query(BpModel)
        .join(BpModel.users)
        .filter_by(id=current_user.id)
        .order_by(BpModel.name)
        .paginate(page=page, per_page=PER_PAGE)
    )
    return render_template('user_blueprints/show.html',
                           blueprints=pagination.items,
                           pagination=pagination)


@bp.route('/user_blueprints/refresh', methods=['POST'])
@login_required
def refresh():
    from esi.download_my_blueprints import download_my_blueprints
    download_my_blueprints(current_user)
    return redirect(url_for('user_blueprints.show'))
