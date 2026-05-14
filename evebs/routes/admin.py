from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from evebs.models import UserActivityLog, LastUpdate, Crontab

bp = Blueprint('admin', __name__)


def require_admin():
    if not current_user.is_authenticated or not current_user.admin:
        return redirect(url_for('admin.denied'))
    return None


@bp.route('/admin_tools')
@login_required
def show():
    guard = require_admin()
    if guard:
        return guard
    last_hourly = LastUpdate.query.filter_by(update_type='hourly').first()
    last_daily = LastUpdate.query.filter_by(update_type='daily').first()
    last_weekly = LastUpdate.query.filter_by(update_type='weekly').first()
    crontabs = Crontab.query.all()
    return render_template('admin/show.html',
                           title='Admin tools',
                           last_hourly=last_hourly,
                           last_daily=last_daily,
                           last_weekly=last_weekly,
                           crontabs=crontabs)


@bp.route('/admin_tools/denied')
@login_required
def denied():
    return render_template('admin/denied.html', title='Access denied')


@bp.route('/admin_tools/activity')
@login_required
def activity():
    guard = require_admin()
    if guard:
        return guard
    logs = UserActivityLog.query.order_by(UserActivityLog.created_at.desc()).limit(200).all()
    return render_template('admin/activity.html', title='Activity log', logs=logs)
