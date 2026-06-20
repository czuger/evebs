import math
from types import SimpleNamespace

from flask import Blueprint as FlaskBlueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import func

from evebs.extensions import db
from evebs.models import (
    EveItem, JitaMinPrice, ProductionList, ReactionList, BlueprintModification,
    UserAsset, UniverseStation, UniverseStructure, UnknownStructure,
)

bp = FlaskBlueprint('components_to_buys', __name__)

# Tech II blueprints (invented from a T1) consume 2% fewer materials.
TECH2_MATERIAL_FACTOR = 0.98


def _compute_components(user) -> list:
    """Aggregate direct materials needed for the user's active production + reaction runs.

    Applies per-user blueprint modification factors (material efficiency) and the Tech II 2%
    reduction for manufacturing; reaction-list entries apply the user's reaction
    material_consumption modifier (<= 0). Material chain is read from
    Blueprint.manufacturing_tree (JSONB column), populated by process/update_blueprints.py.
    Returns a list of SimpleNamespace with eve_item_id, eve_item_name, qtt_to_buy,
    total_cost, required_volume, base_item — matching the template's expected shape.
    """
    production_lists = (
        ProductionList.query
        .filter_by(user_id=user.id)
        .filter(ProductionList.runs_count > 0)
        .all()
    )
    reaction_lists = (
        ReactionList.query
        .filter_by(user_id=user.id)
        .filter(ReactionList.runs_count > 0)
        .all()
    )
    if not production_lists and not reaction_lists:
        return []

    # Build per-blueprint modification factor map
    mods = {
        bm.blueprint_id: bm.percent_modification_value
        for bm in BlueprintModification.query.filter_by(user_id=user.id).all()
    }
    # Reaction material-consumption modifier (always <= 0 → a reduction).
    rxn_factor = 1.0 + (user.reaction_modifications or {}).get('material_consumption', 0) / 100.0

    # Aggregate required quantities per material across all production + reaction entries.
    material_qtys: dict[int, int] = {}
    for pl in production_lists:
        item = pl.eve_item
        if not item or not item.blueprint_id or not item.blueprint:
            continue
        chain = item.blueprint.manufacturing_tree
        if not chain:
            continue
        mod = mods.get(item.blueprint_id, 1.0)
        if item.blueprint.is_invented_from_id is not None:   # Tech II: 2% material reduction
            mod *= TECH2_MATERIAL_FACTOR
        for mat_id_str, mat_data in chain.items():
            mat_id = int(mat_id_str)
            qty = math.ceil(mat_data['quantity'] * pl.runs_count * mod)
            material_qtys[mat_id] = material_qtys.get(mat_id, 0) + qty

    for rl in reaction_lists:
        item = rl.eve_item
        if not item or not item.blueprint_id or not item.blueprint:
            continue
        chain = item.blueprint.manufacturing_tree
        if not chain:
            continue
        for mat_id_str, mat_data in chain.items():
            mat_id = int(mat_id_str)
            qty = math.ceil(mat_data['quantity'] * rl.runs_count * rxn_factor)
            material_qtys[mat_id] = material_qtys.get(mat_id, 0) + qty

    if not material_qtys:
        return []

    mat_ids = list(material_qtys)
    # Bulk-load EveItems and Jita prices in one query each
    item_map = {ei.id: ei for ei in EveItem.query.filter(EveItem.id.in_(mat_ids)).all()}
    jma_map = {jma.id: jma.min_sell_price
               for jma in JitaMinPrice.query.filter(JitaMinPrice.id.in_(mat_ids)).all()}

    results = []
    for mat_id, qty_needed in material_qtys.items():
        mat_item = item_map.get(mat_id)
        if not mat_item:
            continue
        results.append(SimpleNamespace(
            eve_item_id=mat_id,
            eve_item_name=mat_item.name,
            qtt_to_buy=qty_needed,
            total_cost=qty_needed * (jma_map.get(mat_id) or 0),
            required_volume=qty_needed * (mat_item.volume or 0),
            base_item=mat_item.base_item,
        ))

    return sorted(results, key=lambda r: r.eve_item_name)


@bp.route('/components_to_buys')
@login_required
def show():
    user = current_user
    # A fresh visit (no station_id in the query) defaults to the user's saved industry
    # station; selecting an option or Clear submits station_id explicitly and overrides it.
    if 'station_id' in request.args:
        station_id = request.args.get('station_id', type=int)
    else:
        station_id = (user.industry_modifications or {}).get('current_industry_station')

    components = _compute_components(user)

    stations = (
        UniverseStation.query
        .join(UserAsset, UserAsset.universe_station_id == UniverseStation.id)
        .filter(UserAsset.user_id == user.id)
        .distinct().all()
    )
    known_structures = (
        UniverseStructure.query
        .join(UserAsset, UserAsset.universe_structure_id == UniverseStructure.id)
        .filter(UserAsset.user_id == user.id)
        .distinct().all()
    )
    unknown_structures = (
        UnknownStructure.query
        .join(UserAsset, UserAsset.universe_structure_id == UnknownStructure.id)
        .filter(UserAsset.user_id == user.id)
        .distinct().all()
    )

    asset_qty = {}
    if station_id:
        rows = (
            db.session.query(UserAsset.eve_item_id, func.sum(UserAsset.quantity))
            .filter(
                UserAsset.user_id == user.id,
                db.or_(
                    UserAsset.universe_station_id == station_id,
                    UserAsset.universe_structure_id == station_id,
                ),
            )
            .group_by(UserAsset.eve_item_id)
            .all()
        )
        asset_qty = {row[0]: int(row[1]) for row in rows}

    return render_template('components_to_buys/show.html',
                           title='Components to buy',
                           components=components,
                           stations=stations,
                           known_structures=known_structures,
                           unknown_structures=unknown_structures,
                           selected_station_id=station_id,
                           asset_qty=asset_qty,
                           user=user)
