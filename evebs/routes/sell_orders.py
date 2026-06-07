"""Sell orders: margin based on the lowest sell order price in public_trade_orders,
net of the user's personal sales_taxes settings (broker fee + sales tax + safety margin).

Contrast with buy_orders which uses the highest buy order price (instant sell to an
existing buy order). Here the user places a sell order at or below the current market
floor and waits for a buyer — the achievable price is higher, but not guaranteed.
"""
import time
from types import SimpleNamespace

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import text, bindparam

from config import set_logger, PER_PAGE
from evebs.extensions import db
from evebs.models.tables.associations import user_blueprints
from evebs.models.tables.blueprint import Blueprint as BlueprintModel
from evebs.models.tables.bpc_asset import BpcAsset
from evebs.models.tables.eve_item import EveItem
from evebs.models.tables.industry_job import IndustryJob
from evebs.models.tables.user_sale_order import UserSaleOrder
from evebs.utils import SimplePagination

bp = Blueprint('sell_orders', __name__)

_timings = set_logger('timings')

_SELECT = """
SELECT
    uic.item_name,
    uic.item_slug,
    uic.produced_type_id                                                         AS eve_item_id,
    us.name || ' (' || ur.name || ')'                                            AS trade_hub_name,
    ls.universe_system_id,
    uic.mat_cost_per_unit + uic.ind_tax_per_unit                                AS total_cost_per_unit,
    ls.sell_price,
    ls.sell_price * :sell_fee                                                    AS sell_fee_per_unit,
    ls.sell_price * (1.0 - :sell_fee) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit)
                                                                                 AS margin_per_unit,
    CASE WHEN ls.sell_price > 0
         THEN (ls.sell_price * (1.0 - :sell_fee) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit))
              / ls.sell_price
         ELSE 0
    END                                                                          AS margin_pcent,
    ls.sell_volume,
    b.nb_runs * b.prod_qtt                                                       AS full_batch_amount,
    (b.nb_runs * b.prod_qtt)
        * (ls.sell_price * (1.0 - :sell_fee) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit))
                                                                                 AS margin_full_batch
FROM user_industry_costs uic
JOIN lowest_sell ls ON ls.eve_item_id = uic.produced_type_id
JOIN blueprints b ON b.id = uic.blueprint_id
JOIN universe_systems us ON us.id = ls.universe_system_id
JOIN universe_constellations uc ON uc.id = us.universe_constellation_id
JOIN universe_regions ur ON ur.id = uc.universe_region_id
WHERE uic.user_id    = :user_id
  AND uic.activity_type = 'manufacturing'
  AND ls.sell_price * (1.0 - :sell_fee) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit) > 0
  AND CASE WHEN ls.sell_price > 0
       THEN (ls.sell_price * (1.0 - :sell_fee) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit)) / ls.sell_price
       ELSE 0 END >= :min_margin_pcent
  AND (b.nb_runs * b.prod_qtt)
      * (ls.sell_price * (1.0 - :sell_fee) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit)) >= :min_batch_margin
ORDER BY margin_full_batch DESC
"""

# DISTINCT ON gives the single lowest-priced sell order per (item, hub) —
# that is the current market floor, the best price achievable by undercutting.
_SQL = """
WITH lowest_sell AS (
    SELECT DISTINCT ON (eve_item_id, universe_system_id)
        eve_item_id,
        universe_system_id,
        price         AS sell_price,
        volume_remain AS sell_volume
    FROM public_trade_orders
    WHERE is_buy_order = FALSE
      AND eve_item_id IN :item_ids
      AND universe_system_id IN :hub_ids
    ORDER BY eve_item_id, universe_system_id, price ASC
)
""" + _SELECT

# show_selected_items=False: no item filter — all game blueprints via user_industry_costs CROSS JOIN
_SQL_ALL = """
WITH lowest_sell AS (
    SELECT DISTINCT ON (eve_item_id, universe_system_id)
        eve_item_id,
        universe_system_id,
        price         AS sell_price,
        volume_remain AS sell_volume
    FROM public_trade_orders
    WHERE is_buy_order = FALSE
      AND universe_system_id IN :hub_ids
    ORDER BY eve_item_id, universe_system_id, price ASC
)
""" + _SELECT


@bp.route('/sell_orders')
@login_required
def show():
    page = request.args.get('page', 1, type=int)
    user = current_user

    sof = user.sell_orders_filtering or {}
    show_selected = sof.get('show_selected_items', False)

    t0 = time.perf_counter()
    hub_ids = [h.id for h in user.trade_hubs]
    if show_selected:
        item_ids = [ei.id for ei in user.eve_items]
        should_run = bool(item_ids and hub_ids)
    else:
        item_ids = None
        should_run = bool(hub_ids)
    _timings.info('sell_orders.user_items_and_hubs',
                  extra={'duration_ms': (time.perf_counter() - t0) * 1000,
                         'n_items': len(item_ids) if item_ids else -1, 'n_hubs': len(hub_ids)})

    rows = []
    pagination = None

    if should_run:
        st = user.sales_taxes or {}
        sell_fee = (
            st.get('broker_fee_taxes', 0)
            + st.get('sales_taxes', 0)
            + st.get('safety_tax', 0)
        ) / 100.0

        min_margin_pcent = sof.get('min_margin_percent', 20) / 100.0
        min_batch_margin = sof.get('min_batch_margin_amount', 5_000_000)

        sql = _SQL if show_selected else _SQL_ALL
        params = {
            'user_id':          user.id,
            'hub_ids':          hub_ids,
            'sell_fee':         sell_fee,
            'min_margin_pcent': min_margin_pcent,
            'min_batch_margin': min_batch_margin,
        }
        if show_selected:
            params['item_ids'] = item_ids

        bp_hub = bindparam('hub_ids', expanding=True)
        if show_selected:
            bp_item = bindparam('item_ids', expanding=True)
            count_stmt = text(f'SELECT COUNT(*) FROM ({sql}) t').bindparams(bp_item, bp_hub)
            data_stmt  = text(sql + ' LIMIT :limit OFFSET :offset').bindparams(bp_item, bp_hub)
        else:
            count_stmt = text(f'SELECT COUNT(*) FROM ({sql}) t').bindparams(bp_hub)
            data_stmt  = text(sql + ' LIMIT :limit OFFSET :offset').bindparams(bp_hub)

        t0 = time.perf_counter()
        total = db.session.execute(count_stmt, params).scalar() or 0
        _timings.info('sell_orders.count_query',
                      extra={'duration_ms': (time.perf_counter() - t0) * 1000,
                             'total': total})

        t0 = time.perf_counter()
        rows_raw = db.session.execute(
            data_stmt,
            {**params, 'limit': PER_PAGE, 'offset': (page - 1) * PER_PAGE},
        ).mappings().all()
        _timings.info('sell_orders.main_query',
                      extra={'duration_ms': (time.perf_counter() - t0) * 1000,
                             'n_rows': len(rows_raw)})

        rows = [SimpleNamespace(**r) for r in rows_raw]
        if total:
            pagination = SimplePagination(page, PER_PAGE, total)

    t0 = time.perf_counter()
    potential = (
        db.session.query(BpcAsset.eve_item_id, BpcAsset.potential_type)
        .filter(BpcAsset.user_id == user.id, BpcAsset.is_potential == True)
        .all()
    )
    owned_bp_ids = {
        row.produced_type_id for row in
        db.session.query(BlueprintModel.produced_type_id)
        .join(user_blueprints, user_blueprints.c.blueprint_id == BlueprintModel.id)
        .filter(user_blueprints.c.user_id == user.id)
    }
    _timings.info('sell_orders.badge_queries',
                  extra={'duration_ms': (time.perf_counter() - t0) * 1000})
    potential_copy_ids        = {r.eve_item_id for r in potential if r.potential_type == 'copy'}
    potential_invent_ids      = {r.eve_item_id for r in potential if r.potential_type == 'invent'}
    potential_copy_invent_ids = {r.eve_item_id for r in potential if r.potential_type == 'copy_invent'}

    sale_order_item_ids = {
        r.eve_item_id for r in
        db.session.query(UserSaleOrder.eve_item_id)
        .filter(UserSaleOrder.user_id == user.id).all()
    }
    active_job_item_ids = {
        r.product_type_id for r in
        db.session.query(IndustryJob.product_type_id)
        .filter(IndustryJob.user_id == user.id,
                IndustryJob.status.in_(['active', 'paused'])).all()
    }

    return render_template(
        'sell_orders/show.html',
        title='Sell orders (mine)',
        sell_orders=rows,
        pagination=pagination,
        owned_bp_ids=owned_bp_ids,
        potential_copy_ids=potential_copy_ids,
        potential_invent_ids=potential_invent_ids,
        potential_copy_invent_ids=potential_copy_invent_ids,
        sale_order_item_ids=sale_order_item_ids,
        active_job_item_ids=active_job_item_ids,
        user=user,
    )
