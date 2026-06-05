from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from evebs.extensions import db
from evebs.models import InventionList

bp = Blueprint('invention_lists', __name__)


@bp.route('/invention_lists/edit')
@login_required
def edit():
    user = current_user
    invention_lists = InventionList.query.filter_by(user_id=user.id).all()
    return render_template('invention_lists/edit.html',
                           title='Invention list',
                           invention_lists=invention_lists,
                           user=user)


@bp.route('/invention_lists', methods=['POST'])
@login_required
def create():
    user = current_user
    eve_item_id = request.form.get('eve_item_id', type=int)
    universe_system_id = request.form.get('universe_system_id', type=int)
    runs_count = request.form.get('runs_count', 1, type=int)

    existing = InventionList.query.filter_by(
        user_id=user.id, eve_item_id=eve_item_id, universe_system_id=universe_system_id
    ).first()
    if not existing:
        il = InventionList(
            user_id=user.id,
            eve_item_id=eve_item_id,
            universe_system_id=universe_system_id,
            runs_count=runs_count,
        )
        db.session.add(il)
        db.session.commit()
        flash('Added to invention list.', 'success')
    else:
        flash('Already in invention list.', 'info')
    return redirect(request.referrer or url_for('invention_lists.edit'))


@bp.route('/remove_invention_list_check', methods=['POST'])
@login_required
def remove_check():
    user = current_user
    universe_system_id = request.form.get('universe_system_id', type=int)
    eve_item_id = request.form.get('eve_item_id', type=int)
    InventionList.query.filter_by(
        user_id=user.id, universe_system_id=universe_system_id, eve_item_id=eve_item_id
    ).delete()
    db.session.commit()
    return ('', 204)
