from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from evebs.extensions import db
from evebs.models import CopyList

bp = Blueprint('copy_lists', __name__)


@bp.route('/copy_lists/edit')
@login_required
def edit():
    user = current_user
    copy_lists = CopyList.query.filter_by(user_id=user.id).all()
    return render_template('copy_lists/edit.html',
                           title='Copy list',
                           copy_lists=copy_lists,
                           user=user)


@bp.route('/copy_lists', methods=['POST'])
@login_required
def create():
    user = current_user
    eve_item_id = request.form.get('eve_item_id', type=int)
    universe_system_id = request.form.get('universe_system_id', type=int)
    runs_count = request.form.get('runs_count', 1, type=int)

    existing = CopyList.query.filter_by(
        user_id=user.id, eve_item_id=eve_item_id, universe_system_id=universe_system_id
    ).first()
    if not existing:
        cl = CopyList(
            user_id=user.id,
            eve_item_id=eve_item_id,
            universe_system_id=universe_system_id,
            runs_count=runs_count,
        )
        db.session.add(cl)
        db.session.commit()
        flash('Added to copy list.', 'success')
    else:
        flash('Already in copy list.', 'info')
    return redirect(request.referrer or url_for('copy_lists.edit'))


@bp.route('/copy_lists/clear_all', methods=['POST'])
@login_required
def clear_all():
    CopyList.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Copy list cleared.', 'success')
    return redirect(url_for('copy_lists.edit'))


@bp.route('/remove_copy_list_check', methods=['POST'])
@login_required
def remove_check():
    user = current_user
    universe_system_id = request.form.get('universe_system_id', type=int)
    eve_item_id = request.form.get('eve_item_id', type=int)
    CopyList.query.filter_by(
        user_id=user.id, universe_system_id=universe_system_id, eve_item_id=eve_item_id
    ).delete()
    db.session.commit()
    return ('', 204)
