from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from evebs.extensions import db
from evebs.models import BpcAsset, Blueprint as BpModel, MarketPrice

bp = Blueprint('my_blueprints', __name__)


@bp.route('/my_blueprints')
@login_required
def show():
    """Rank owned blueprints by benefit (adjusted result price minus fabrication cost)."""
    rows_raw = (
        db.session.query(BpcAsset, BpModel)
        .join(BpModel, BpcAsset.eve_item_id == BpModel.id)
        .filter(BpcAsset.user_id == current_user.id)
        .options(
            joinedload(BpModel.blueprint_materials),
        )
        .all()
    )

    type_ids = set()
    for _asset, blueprint in rows_raw:
        type_ids.add(blueprint.produced_type_id)
        for mat in blueprint.blueprint_materials:
            type_ids.add(mat.universe_type_id)

    market_prices = {
        mp.type_id: mp
        for mp in MarketPrice.query.filter(MarketPrice.type_id.in_(type_ids)).all()
    }

    rows = []
    for asset, blueprint in rows_raw:
        fab_cost = sum(
            mat.required_qtt * market_prices[mat.universe_type_id].adjusted_price
            for mat in blueprint.blueprint_materials
            if mat.universe_type_id in market_prices
            and market_prices[mat.universe_type_id].adjusted_price is not None
        )
        result_mp = market_prices.get(blueprint.produced_type_id)
        result_price = result_mp.adjusted_price if result_mp and result_mp.adjusted_price else None
        benefit = result_price * blueprint.prod_qtt - fab_cost if result_price is not None else None
        rows.append({
            'asset': asset,
            'blueprint': blueprint,
            'fab_cost': fab_cost,
            'result_price': result_price,
            'benefit': benefit,
        })

    rows.sort(key=lambda r: r['benefit'] if r['benefit'] is not None else float('-inf'), reverse=True)

    return render_template('my_blueprints/show.html', rows=rows, title='My blueprints')
