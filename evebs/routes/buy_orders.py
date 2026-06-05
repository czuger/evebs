from types import SimpleNamespace

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import text, bindparam

from evebs.extensions import db
from evebs.models.tables.bpc_asset import BpcAsset
from evebs.utils import SimplePagination

bp = Blueprint('buy_orders', __name__)
PER_PAGE = 12
SELL_TAX_RATE = 0.05

# DISTINCT ON gives the single highest-priced buy order per (item, hub) —
# its volume_remain is the volume of that one order, not the sum of all orders.
_SQL = """
WITH highest_buy AS (
    SELECT DISTINCT ON (eve_item_id, universe_system_id)
        eve_item_id,
        universe_system_id,
        price        AS buy_price,
        volume_remain AS buy_volume
    FROM public_trade_orders
    WHERE is_buy_order = TRUE
      AND eve_item_id IN :item_ids
      AND universe_system_id IN :hub_ids
    ORDER BY eve_item_id, universe_system_id, price DESC
)
SELECT
    uic.item_name,
    uic.item_slug,
    uic.produced_type_id                                                        AS eve_item_id,
    us.name || ' (' || ur.name || ')'                                           AS trade_hub_name,
    hb.universe_system_id,
    uic.mat_cost_per_unit + uic.ind_tax_per_unit                               AS total_cost_per_unit,
    hb.buy_price,
    hb.buy_price * :sell_tax                                                    AS sell_tax_per_unit,
    hb.buy_price * (1.0 - :sell_tax) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit)
                                                                                AS margin_per_unit,
    CASE WHEN hb.buy_price > 0
         THEN (hb.buy_price * (1.0 - :sell_tax) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit))
              / hb.buy_price
         ELSE 0
    END                                                                         AS margin_pcent,
    hb.buy_volume,
    b.nb_runs * b.prod_qtt                                                      AS full_batch_amount,
    (b.nb_runs * b.prod_qtt)
        * (hb.buy_price * (1.0 - :sell_tax) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit))
                                                                                AS margin_full_batch
FROM user_industry_costs uic
JOIN highest_buy hb ON hb.eve_item_id = uic.produced_type_id
JOIN blueprints b ON b.id = uic.blueprint_id
JOIN universe_systems us ON us.id = hb.universe_system_id
JOIN universe_constellations uc ON uc.id = us.universe_constellation_id
JOIN universe_regions ur ON ur.id = uc.universe_region_id
WHERE uic.user_id    = :user_id
  AND uic.activity_type = 'manufacturing'
  AND hb.buy_price * (1.0 - :sell_tax) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit) > 0
ORDER BY margin_full_batch DESC
"""


@bp.route('/buy_orders')
@login_required
def show():
    page = request.args.get('page', 1, type=int)
    user = current_user

    watched_item_ids = [ei.id for ei in user.eve_items if ei.blueprint]
    hub_ids          = [h.id for h in user.trade_hubs]

    rows = []
    pagination = None

    if watched_item_ids and hub_ids:
        params = {
            'user_id':  user.id,
            'item_ids': watched_item_ids,
            'hub_ids':  hub_ids,
            'sell_tax': SELL_TAX_RATE,
        }
        bp_item = bindparam('item_ids', expanding=True)
        bp_hub  = bindparam('hub_ids',  expanding=True)

        stmt = text(_SQL).bindparams(bp_item, bp_hub)

        total = db.session.execute(
            text(f'SELECT COUNT(*) FROM ({_SQL}) t').bindparams(bp_item, bp_hub),
            params,
        ).scalar() or 0

        rows_raw = db.session.execute(
            text(_SQL + ' LIMIT :limit OFFSET :offset').bindparams(bp_item, bp_hub),
            {**params, 'limit': PER_PAGE, 'offset': (page - 1) * PER_PAGE},
        ).mappings().all()

        rows = [SimpleNamespace(**r) for r in rows_raw]
        if total:
            pagination = SimplePagination(page, PER_PAGE, total)

    potential = (
        db.session.query(BpcAsset.eve_item_id, BpcAsset.potential_type)
        .filter(BpcAsset.user_id == user.id, BpcAsset.is_potential == True)
        .all()
    )
    owned_bp_ids          = {b.produced_type_id for b in user.blueprints}
    potential_copy_ids        = {r.eve_item_id for r in potential if r.potential_type == 'copy'}
    potential_invent_ids      = {r.eve_item_id for r in potential if r.potential_type == 'invent'}
    potential_copy_invent_ids = {r.eve_item_id for r in potential if r.potential_type == 'copy_invent'}

    return render_template(
        'buy_orders/show.html',
        title='Buy orders',
        buy_orders=rows,
        pagination=pagination,
        owned_bp_ids=owned_bp_ids,
        potential_copy_ids=potential_copy_ids,
        potential_invent_ids=potential_invent_ids,
        potential_copy_invent_ids=potential_copy_invent_ids,
        user=user,
    )
