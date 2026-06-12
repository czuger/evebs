from flask import Blueprint as FlaskBlueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import case, nullslast, func

from config import PER_PAGE
from esi.download_my_industry_jobs import DownloadMyIndustryJobs
from evebs.models import IndustryJob, EveItem, ACTIVITY_LABELS
from evebs.utils import SimplePagination

bp = FlaskBlueprint('industry_jobs', __name__)


@bp.route('/industry_jobs')
@login_required
def show():
    page = request.args.get('page', 1, type=int)

    base_query = (
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
    )

    total = base_query.count()
    jobs = base_query.limit(PER_PAGE).offset((page - 1) * PER_PAGE).all()
    pagination = SimplePagination(page, PER_PAGE, total) if total else None

    active_counts = (
        IndustryJob.query.with_entities(IndustryJob.activity_id, func.count())
        .filter(IndustryJob.user_id == current_user.id,
                IndustryJob.status == 'active')
        .group_by(IndustryJob.activity_id)
        .all()
    )
    active_counts_by_label = {
        ACTIVITY_LABELS.get(activity_id, activity_id): count
        for activity_id, count in active_counts
    }

    product_type_ids = {j.product_type_id for j in jobs if j.product_type_id}
    items_by_type_id = {
        item.id: item
        for item in EveItem.query.filter(EveItem.id.in_(product_type_ids)).all()
    } if product_type_ids else {}

    return render_template(
        'industry_jobs/show.html',
        jobs=jobs,
        pagination=pagination,
        active_counts_by_label=active_counts_by_label,
        activity_labels=ACTIVITY_LABELS,
        items_by_type_id=items_by_type_id,
        user=current_user,
    )


@bp.route('/industry_jobs/refresh', methods=['POST'])
@login_required
def refresh():
    DownloadMyIndustryJobs().update(current_user)
    return redirect(url_for('industry_jobs.show'))
