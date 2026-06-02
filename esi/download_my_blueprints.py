import logging
from datetime import datetime

from evebs.extensions import db
from esi.client import EsiClient

logger = logging.getLogger(__name__)


def download_my_blueprints(user):
    from evebs.models import Blueprint
    from evebs.models.tables.associations import user_blueprints

    client = EsiClient(f'characters/{user.uid}/assets/')
    if not client.set_auth_token(user):
        logger.warning('Could not set auth token for user %s', user.id)
        return False

    pages = client.get_all_pages()
    if pages is None:
        logger.warning('No data returned from ESI for user %s', user.id)
        return False

    known = {bp.id for bp in Blueprint.query.all()}
    bp_ids = list({a['type_id'] for a in pages if a.get('type_id') in known})

    db.session.execute(
        user_blueprints.delete().where(user_blueprints.c.user_id == user.id)
    )
    for bp_id in bp_ids:
        db.session.execute(
            user_blueprints.insert().values(user_id=user.id, blueprint_id=bp_id)
        )

    user.last_blueprints_download = datetime.utcnow()
    db.session.commit()
    logger.info('Blueprints refreshed for user %s: %d found', user.id, len(bp_ids))
    return True
