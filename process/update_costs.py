"""Update item costs: base items from weekly avg, crafted items from Blueprint.manufacturing_cost."""
import logging
from evebs.extensions import db
from evebs.models import EveItem, Blueprint, Constant
from datetime import datetime

logger = logging.getLogger(__name__)


def update_base_item_costs():
    """Base items: cost = weekly_avg_price (Jita)."""
    logger.debug('Updating base item costs...')
    from sqlalchemy import text
    db.session.execute(text(
        "UPDATE eve_items SET cost = weekly_avg_price, updated_at = :now "
        "WHERE base_item = TRUE"
    ), {'now': datetime.utcnow()})
    db.session.commit()
    logger.debug('Base item costs updated.')


def update_crafted_item_costs(production_level):
    """Crafted items: cost = blueprint.manufacturing_cost * taxes / prod_qtt."""
    logger.debug('Updating crafted item costs (level %s)...', production_level)
    taxes_const = Constant.query.filter_by(libe='taxes').first()
    if not taxes_const:
        logger.warning('Taxes constant not set. Skipping.')
        return
    taxes = taxes_const.f_value

    items = EveItem.query.filter_by(
        base_item=False, production_level=production_level
    ).filter(EveItem.blueprint_id.isnot(None)).all()

    for item in items:
        bp = item.blueprint
        if not bp or bp.manufacturing_cost is None:
            item.cost = None
            continue
        item.cost = (bp.manufacturing_cost * taxes) / bp.prod_qtt if bp.prod_qtt else None

    db.session.commit()
    logger.debug('Crafted item costs (level %s) updated.', production_level)


def update_all_costs():
    update_base_item_costs()
    # Update crafted items level by level (base first, then higher)
    max_levels = db.session.execute(
        db.select(db.func.max(EveItem.production_level)).filter(
            EveItem.base_item.is_(False), EveItem.blueprint_id.isnot(None)
        )
    ).scalar() or 5
    for level in range(1, max_levels + 1):
        update_crafted_item_costs(level)
