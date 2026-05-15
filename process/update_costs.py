"""Update item costs: base items from weekly avg, crafted items from components."""
import math
from evebs.extensions import db
from evebs.models import EveItem, Blueprint, BlueprintMaterial, Constant
from datetime import datetime


def update_base_item_costs():
    """Base items: cost = weekly_avg_price (Jita)."""
    print('Updating base item costs...')
    from sqlalchemy import text
    db.session.execute(text(
        "UPDATE eve_items SET cost = weekly_avg_price, updated_at = :now "
        "WHERE base_item = TRUE"
    ), {'now': datetime.utcnow()})
    db.session.commit()
    print('Base item costs updated.')


def update_crafted_item_costs(production_level):
    """Crafted items: cost = sum(component_cost * qty) * taxes / prod_qtt."""
    print(f'Updating crafted item costs (level {production_level})...')
    taxes_const = Constant.query.filter_by(libe='taxes').first()
    if not taxes_const:
        print('Taxes constant not set. Skipping.')
        return
    taxes = taxes_const.f_value

    items = EveItem.query.filter_by(
        base_item=False, production_level=production_level
    ).filter(EveItem.blueprint_id.isnot(None)).all()

    for item in items:
        bp = item.blueprint
        if not bp:
            continue
        total = 0.0
        infinite = False
        for mat in bp.blueprint_materials:
            comp = mat.eve_item
            if comp is None or comp.cost is None:
                infinite = True
                break
            total += mat.required_qtt * comp.cost
        if infinite:
            item.cost = float('inf')
        else:
            item.cost = (total * taxes) / bp.prod_qtt if bp.prod_qtt else float('inf')

    db.session.commit()
    print(f'Crafted item costs (level {production_level}) updated.')


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
