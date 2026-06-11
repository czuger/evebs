import time
from types import SimpleNamespace

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import text, bindparam

from evebs.extensions import db
from evebs.models.tables.associations import user_blueprints
from evebs.models.tables.blueprint import Blueprint as BlueprintModel
from evebs.models.tables.user_asset import UserAsset
from evebs.models.tables.eve_item import EveItem
from evebs.models.tables.industry_job import IndustryJob
from evebs.models.tables.user_sale_order import UserSaleOrder
from config import set_logger, PER_PAGE
from evebs.utils import SimplePagination, active_job_item_sets

bp = Blueprint('buy_orders', __name__)

_timings = set_logger('timings')

_SELECT = """
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
  AND CASE WHEN hb.buy_price > 0
       THEN (hb.buy_price * (1.0 - :sell_tax) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit)) / hb.buy_price
       ELSE 0 END >= :min_margin_pcent
  AND (b.nb_runs * b.prod_qtt)
      * (hb.buy_price * (1.0 - :sell_tax) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit)) >= :min_batch_margin
ORDER BY margin_full_batch DESC
"""

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
""" + _SELECT

# show_selected_items=False: no item filter — all game blueprints via user_industry_costs CROSS JOIN
_SQL_ALL = """
WITH highest_buy AS (
    SELECT DISTINCT ON (eve_item_id, universe_system_id)
        eve_item_id,
        universe_system_id,
        price        AS buy_price,
        volume_remain AS buy_volume
    FROM public_trade_orders
    WHERE is_buy_order = TRUE
      AND universe_system_id IN :hub_ids
    ORDER BY eve_item_id, universe_system_id, price DESC
)
""" + _SELECT


@bp.route('/buy_orders')
@login_required
def show():
    page = request.args.get('page', 1, type=int)
    user = current_user

    bof = user.buy_order_filtering or {}
    show_selected = bof.get('show_selected_items', False)

    t0 = time.perf_counter()
    hub_ids = [h.id for h in user.trade_hubs]
    if show_selected:
        item_ids = [ei.id for ei in user.eve_items]
        should_run = bool(item_ids and hub_ids)
    else:
        item_ids = None
        should_run = bool(hub_ids)
    _timings.info('buy_orders.user_items_and_hubs',
                  extra={'duration_ms': (time.perf_counter() - t0) * 1000,
                         'n_items': len(item_ids) if item_ids else -1, 'n_hubs': len(hub_ids)})

    rows = []
    pagination = None

    if should_run:
        st = user.sales_taxes or {}
        sell_tax = (
            st.get('sales_taxes', 0)
            + st.get('safety_tax', 0)
        ) / 100.0

        min_margin_pcent = bof.get('min_margin_percent', 20) / 100.0
        min_batch_margin = bof.get('min_batch_margin_amount', 5_000_000)

        sql = _SQL if show_selected else _SQL_ALL
        params = {
            'user_id':          user.id,
            'hub_ids':          hub_ids,
            'sell_tax':         sell_tax,
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
        _timings.info('buy_orders.count_query',
                      extra={'duration_ms': (time.perf_counter() - t0) * 1000,
                             'total': total})

        t0 = time.perf_counter()
        rows_raw = db.session.execute(
            data_stmt,
            {**params, 'limit': PER_PAGE, 'offset': (page - 1) * PER_PAGE},
        ).mappings().all()
        _timings.info('buy_orders.main_query',
                      extra={'duration_ms': (time.perf_counter() - t0) * 1000,
                             'n_rows': len(rows_raw)})

        rows = [SimpleNamespace(**r) for r in rows_raw]
        if total:
            pagination = SimplePagination(page, PER_PAGE, total)

    t0 = time.perf_counter()
    potential = (
        db.session.query(UserAsset.eve_item_id, UserAsset.potential_type)
        .filter(UserAsset.user_id == user.id, UserAsset.is_potential == True)
        .all()
    )
    owned_bp_ids = {
        row.produced_type_id for row in
        db.session.query(BlueprintModel.produced_type_id)
        .join(user_blueprints, user_blueprints.c.blueprint_id == BlueprintModel.id)
        .filter(user_blueprints.c.user_id == user.id)
    }
    _timings.info('buy_orders.badge_queries',
                  extra={'duration_ms': (time.perf_counter() - t0) * 1000})
    potential_copy_ids        = {r.eve_item_id for r in potential if r.potential_type == 'copy'}
    potential_invent_ids      = {r.eve_item_id for r in potential if r.potential_type == 'invent'}
    potential_copy_invent_ids = {r.eve_item_id for r in potential if r.potential_type == 'copy_invent'}

    sale_order_item_ids = {
        r.eve_item_id for r in
        db.session.query(UserSaleOrder.eve_item_id)
        .filter(UserSaleOrder.user_id == user.id).all()
    }
    active_jobs = (
        db.session.query(IndustryJob.activity_id,
                         IndustryJob.product_type_id,
                         IndustryJob.blueprint_type_id)
        .filter(IndustryJob.user_id == user.id,
                IndustryJob.status.in_(['active', 'paused'])).all()
    )
    active_job_item_ids, copying_item_ids, inventing_item_ids = active_job_item_sets(active_jobs)

    return render_template(
        'buy_orders/show.html',
        title='Buy orders',
        buy_orders=rows,
        pagination=pagination,
        owned_bp_ids=owned_bp_ids,
        potential_copy_ids=potential_copy_ids,
        potential_invent_ids=potential_invent_ids,
        potential_copy_invent_ids=potential_copy_invent_ids,
        sale_order_item_ids=sale_order_item_ids,
        active_job_item_ids=active_job_item_ids,
        copying_item_ids=copying_item_ids,
        inventing_item_ids=inventing_item_ids,
        user=user,
    )
