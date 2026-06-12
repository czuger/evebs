import json
from flask import Blueprint as FlaskBlueprint, render_template, request, redirect, url_for, abort, flash
from flask_login import login_required, current_user

from evebs.extensions import db
from evebs.models import EveItemsSavedList, EveItem

bp = FlaskBlueprint('eve_items_saved_lists', __name__)


@bp.route('/eve_items_saved_lists')
@login_required
def index():
    lists = EveItemsSavedList.query.filter_by(user_id=current_user.id).all()
    return render_template('eve_items_saved_lists/index.html',
                           title='My saved lists',
                           saved_lists=lists)


@bp.route('/eve_items_saved_lists/new')
@login_required
def new():
    return render_template('eve_items_saved_lists/new.html', title='Save current list')


@bp.route('/eve_items_saved_lists', methods=['POST'])
@login_required
def create():
    user = current_user
    description = request.form.get('description', '').strip()
    if not description:
        flash('Description is required.')
        return redirect(url_for('eve_items_saved_lists.new'))
    saved = EveItemsSavedList(
        user_id=user.id,
        description=description,
        saved_ids=json.dumps(user.eve_item_ids),
    )
    db.session.add(saved)
    db.session.commit()
    return redirect(url_for('eve_items_saved_lists.index'))


@bp.route('/eve_items_saved_lists/<int:list_id>/load')
@login_required
def load(list_id):
    user = current_user
    saved = EveItemsSavedList.query.filter_by(id=list_id, user_id=user.id).first_or_404()
    ids = saved.get_ids()
    items = EveItem.query.filter(EveItem.id.in_(ids)).all()
    user.eve_items.clear()
    for item in items:
        user.eve_items.append(item)
    db.session.commit()
    flash(f'List "{saved.description}" loaded.')
    return redirect(url_for('list_items.show'))


@bp.route('/eve_items_saved_lists/clear')
@login_required
def clear():
    current_user.eve_items.clear()
    db.session.commit()
    return redirect(url_for('list_items.show'))


@bp.route('/eve_items_saved_lists/<int:list_id>/delete', methods=['POST'])
@login_required
def delete(list_id):
    saved = EveItemsSavedList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    db.session.delete(saved)
    db.session.commit()
    return redirect(url_for('eve_items_saved_lists.index'))
