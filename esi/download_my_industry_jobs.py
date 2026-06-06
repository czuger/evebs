import logging
from datetime import datetime

from esi.client import EsiClient

logger = logging.getLogger(__name__)


class DownloadMyIndustryJobs:
    def update(self, user):
        if user.locked:
            logger.debug('%s is locked. Skipping.', user.name)
            return

        client = EsiClient(f'characters/{user.uid}/industry/jobs/', params={'include_completed': 'true'})
        if not client.set_auth_token(user):
            return

        pages = client.get_all_pages()
        if not pages:
            user.locked = True
            from evebs.extensions import db
            db.session.commit()
            return

        from evebs.models import IndustryJob
        from evebs.extensions import db

        existing = {j.job_id: j for j in IndustryJob.query.filter_by(user_id=user.id).all()}
        seen_job_ids = set()

        for page in pages:
            job_id = page['job_id']
            seen_job_ids.add(job_id)

            job = existing.get(job_id)
            if not job:
                job = IndustryJob(user_id=user.id, job_id=job_id)
                db.session.add(job)

            job.installer_id           = page.get('installer_id')
            job.facility_id            = page.get('facility_id')
            job.station_id             = page.get('station_id')
            job.activity_id            = page['activity_id']
            job.blueprint_id           = page.get('blueprint_id')
            job.blueprint_type_id      = page.get('blueprint_type_id')
            job.blueprint_location_id  = page.get('blueprint_location_id')
            job.output_location_id     = page.get('output_location_id')
            job.runs                   = page.get('runs')
            job.cost                   = page.get('cost')
            job.licensed_runs          = page.get('licensed_runs')
            job.probability            = page.get('probability')
            job.product_type_id        = page.get('product_type_id')
            job.status                 = page['status']
            job.duration               = page.get('duration')
            job.start_date             = _parse_dt(page.get('start_date'))
            job.end_date               = _parse_dt(page.get('end_date'))
            job.pause_date             = _parse_dt(page.get('pause_date'))
            job.completed_date         = _parse_dt(page.get('completed_date'))
            job.completed_character_id = page.get('completed_character_id')
            job.successful_runs        = page.get('successful_runs')

        stale_ids = set(existing) - seen_job_ids
        if stale_ids:
            IndustryJob.query.filter(
                IndustryJob.user_id == user.id,
                IndustryJob.job_id.in_(stale_ids),
            ).delete(synchronize_session=False)

        user.download_industry_jobs_running = False
        user.last_industry_jobs_download = datetime.utcnow()
        db.session.commit()


def _parse_dt(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
