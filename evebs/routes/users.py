from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from evebs.extensions import db

bp = Blueprint('users', __name__)


@bp.route('/users/edit')
@login_required
def edit():
    """Render the user settings form."""
    return render_template('users/edit.html',
                           title='Editing user',
                           user=current_user)


@bp.route('/users', methods=['POST'])
@login_required
def update():
    """Persist user preference changes."""
    user = current_user

    raw_amount = request.form.get('min_amount_for_advice', '')
    raw_amount = raw_amount.replace(' ', '')

    try:
        user.min_pcent_for_advice = int(request.form.get('min_pcent_for_advice', user.min_pcent_for_advice))
        user.min_amount_for_advice = int(raw_amount) if raw_amount else user.min_amount_for_advice
        user.vol_month_pcent = int(request.form.get('vol_month_pcent', user.vol_month_pcent))
        user.batch_cap = request.form.get('batch_cap') == 'on'
        user.batch_cap_multiplier = int(request.form.get('batch_cap_multiplier', user.batch_cap_multiplier))
    except (ValueError, TypeError):
        flash('Invalid input.')
        return redirect(url_for('users.edit'))

    db.session.commit()
    flash('User updated successfully.')
    return redirect(url_for('users.edit'))
