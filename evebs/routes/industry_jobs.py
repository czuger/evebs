from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import case, nullslast

from evebs.models import IndustryJob, EveItem, ACTIVITY_LABELS

bp = Blueprint('industry_jobs', __name__)


@bp.route('/industry_jobs')
@login_required
def show():
    jobs = (
        IndustryJob.query
        .filter_by(user_id=current_user.id)
        .order_by(
            case(
                (IndustryJob.status == 'active', 0),
                (IndustryJob.status == 'paused', 1),
                else_=2,
            ),
            nullslast(case(
                (IndustryJob.status.in_(['active', 'paused']), IndustryJob.end_date),
                else_=None,
            ).asc()),
            nullslast(case(
                (IndustryJob.status.notin_(['active', 'paused']), IndustryJob.end_date),
                else_=None,
            ).desc()),
        )
        .all()
    )
    product_type_ids = {j.product_type_id for j in jobs if j.product_type_id}
    items_by_type_id = {
        item.id: item
        for item in EveItem.query.filter(EveItem.id.in_(product_type_ids)).all()
    } if product_type_ids else {}

    return render_template(
        'industry_jobs/show.html',
        jobs=jobs,
        activity_labels=ACTIVITY_LABELS,
        items_by_type_id=items_by_type_id,
        user=current_user,
    )


@bp.route('/industry_jobs/refresh', methods=['POST'])
@login_required
def refresh():
    from esi.download_my_industry_jobs import DownloadMyIndustryJobs
    DownloadMyIndustryJobs().update(current_user)
    return redirect(url_for('industry_jobs.show'))
