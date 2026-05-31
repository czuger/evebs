from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from evebs.extensions import db
from evebs.models import ProductionList, EveItem

bp = Blueprint('production_lists', __name__)


@bp.route('/production_lists/edit')
@login_required
def edit():
    user = current_user
    production_lists = ProductionList.query.filter_by(user_id=user.id).all()
    return render_template('production_lists/edit.html',
                           title='Production list',
                           production_lists=production_lists,
                           user=user)


@bp.route('/production_lists', methods=['POST'])
@login_required
def create():
    user = current_user
    eve_item_id = request.form.get('eve_item_id', type=int)
    universe_system_id = request.form.get('universe_system_id', type=int)
    runs_count = request.form.get('runs_count', 1, type=int)

    existing = ProductionList.query.filter_by(
        user_id=user.id, eve_item_id=eve_item_id, universe_system_id=universe_system_id
    ).first()
    if not existing:
        pl = ProductionList(
            user_id=user.id,
            eve_item_id=eve_item_id,
            universe_system_id=universe_system_id,
            runs_count=runs_count,
        )
        db.session.add(pl)
        db.session.commit()
    return redirect(url_for('production_lists.edit'))


@bp.route('/production_lists/update', methods=['POST'])
@login_required
def update():
    user = current_user
    for key, value in request.form.items():
        if key.startswith('runs_count_'):
            pl_id = int(key.split('_')[-1])
            pl = ProductionList.query.get(pl_id)
            if pl and pl.user_id == user.id:
                try:
                    pl.runs_count = int(value)
                except ValueError:
                    pass
    db.session.commit()
    return redirect(url_for('production_lists.edit'))


@bp.route('/remove_production_list_check', methods=['POST'])
@login_required
def remove_check():
    user = current_user
    universe_system_id = request.form.get('universe_system_id', type=int)
    eve_item_id = request.form.get('eve_item_id', type=int)
    ProductionList.query.filter_by(
        user_id=user.id, universe_system_id=universe_system_id, eve_item_id=eve_item_id
    ).delete()
    db.session.commit()
    return ('', 204)
