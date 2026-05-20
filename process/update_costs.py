"""Update item costs: base items from weekly avg, crafted items from components."""
import math
from sqlalchemy import text
from evebs.extensions import db
from evebs.models import UniverseType, Blueprint, BlueprintMaterial, Constant


def update_base_item_costs():
    """Base items: cost = weekly_avg_price (Jita)."""
    print('Updating base item costs...')
    from sqlalchemy import text
    db.session.execute(text(
        "UPDATE universe_types SET cost = weekly_avg_price WHERE base_item = TRUE"
    ))
    db.session.commit()
    print('Base item costs updated.')


def update_crafted_item_costs(production_level=None):
    """Crafted items: cost = sum(component_cost * qty) * taxes / prod_qtt."""
    print('Updating crafted item costs...')
    taxes_const = Constant.query.filter_by(libe='taxes').first()
    if not taxes_const:
        print('Taxes constant not set. Skipping.')
        return
    taxes = taxes_const.f_value

    items = (UniverseType.query
             .filter_by(base_item=False)
             .join(Blueprint, Blueprint.produced_type_id == UniverseType.id)
             .all())

    for item in items:
        bp = item.blueprint
        if not bp:
            continue
        total = 0.0
        infinite = False
        for mat in bp.blueprint_materials:
            comp = mat.universe_type
            if comp is None or comp.cost is None:
                infinite = True
                break
            total += mat.required_qtt * comp.cost
        if infinite:
            item.cost = float('inf')
        else:
            item.cost = (total * taxes) / bp.prod_qtt if bp.prod_qtt else float('inf')

    db.session.commit()
    print('Crafted item costs updated.')


def update_all_costs():
    """Run base item costs then crafted item costs."""
    update_base_item_costs()
    update_crafted_item_costs(production_level=None)
