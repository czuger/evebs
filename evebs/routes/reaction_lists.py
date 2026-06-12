from flask import Blueprint as FlaskBlueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from evebs.extensions import db
from evebs.models import ReactionList

bp = FlaskBlueprint('reaction_lists', __name__)


@bp.route('/reaction_lists/edit')
@login_required
def edit():
    user = current_user
    reaction_lists = ReactionList.query.filter_by(user_id=user.id).all()
    return render_template('reaction_lists/edit.html',
                           title='Reaction list',
                           reaction_lists=reaction_lists,
                           user=user)


@bp.route('/reaction_lists', methods=['POST'])
@login_required
def create():
    user = current_user
    eve_item_id = request.form.get('eve_item_id', type=int)
    runs_count = request.form.get('runs_count', 1, type=int)

    existing = ReactionList.query.filter_by(user_id=user.id, eve_item_id=eve_item_id).first()
    if not existing:
        db.session.add(ReactionList(user_id=user.id, eve_item_id=eve_item_id, runs_count=runs_count))
        db.session.commit()
        flash('Added to reaction list.', 'success')
    else:
        flash('Already in reaction list.', 'info')
    return redirect(request.referrer or url_for('reaction_lists.edit'))


@bp.route('/reaction_lists/update', methods=['POST'])
@login_required
def update():
    user = current_user
    for key, value in request.form.items():
        if key.startswith('runs_count_'):
            rl_id = int(key.split('_')[-1])
            rl = ReactionList.query.get(rl_id)
            if rl and rl.user_id == user.id:
                try:
                    rl.runs_count = int(value)
                except ValueError:
                    pass
    db.session.commit()
    return redirect(url_for('reaction_lists.edit'))


@bp.route('/reaction_lists/clear_all', methods=['POST'])
@login_required
def clear_all():
    ReactionList.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Reaction list cleared.', 'success')
    return redirect(url_for('reaction_lists.edit'))


@bp.route('/remove_reaction_list_check', methods=['POST'])
@login_required
def remove_check():
    user = current_user
    eve_item_id = request.form.get('eve_item_id', type=int)
    ReactionList.query.filter_by(user_id=user.id, eve_item_id=eve_item_id).delete()
    db.session.commit()
    flash('Removed from reaction list.', 'success')
    return redirect(url_for('reaction_lists.edit'))
