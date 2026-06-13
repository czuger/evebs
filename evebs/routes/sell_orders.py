"""Sell orders: margin based on the 3-day Jita **price forecast** (the 7-day-window
`forecast_7d` from `jita_price_forecast_linear_regression`), net of the user's personal
sales_taxes settings (broker fee + sales tax + safety margin). The "Forecast vol." column
shows the matching Jita **volume forecast** (`jita_volume_forecast_linear_regression`).

Forward-looking and Jita-only: rows are the items the user owns a manufacturing blueprint
for that have a Jita forecast — there is no per-hub / live-market dependency here (contrast
with buy_orders, which uses the highest live buy order in public_trade_orders).
"""
import time
from types import SimpleNamespace

from flask import Blueprint as FlaskBlueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import text, bindparam

from config import set_logger, PER_PAGE
from evebs.extensions import db
from evebs.models.tables.associations import user_blueprints
from evebs.models.tables.blueprint import Blueprint as BlueprintModel
from evebs.models.tables.user_asset import UserAsset
from evebs.models.tables.eve_item import EveItem
from evebs.models.tables.industry_job import IndustryJob
from evebs.models.tables.user_sale_order import UserSaleOrder
from evebs.utils import SimplePagination, active_job_item_sets

bp = FlaskBlueprint('sell_orders', __name__)

_timings = set_logger('timings')

# `sell_price` / `sell_volume` are the Jita 3-day forecast (price / volume) `forecast_7d`
# values at the +3d horizon — kept under those aliases so the template stays simple.
# `{item_filter}` is empty, or restricts to the user's selected items when show_selected.
JITA_SYSTEM_ID = 30000142

_SQL = """
SELECT
    uic.item_name,
    uic.item_slug,
    uic.produced_type_id                                                         AS eve_item_id,
    {jita}                                                                       AS universe_system_id,
    uic.mat_cost_per_unit + uic.ind_tax_per_unit                                AS total_cost_per_unit,
    pf.forecast_7d                                                               AS sell_price,
    pf.forecast_7d * :sell_fee                                                   AS sell_fee_per_unit,
    pf.forecast_7d * (1.0 - :sell_fee) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit)
                                                                                 AS margin_per_unit,
    CASE WHEN pf.forecast_7d > 0
         THEN (pf.forecast_7d * (1.0 - :sell_fee) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit))
              / pf.forecast_7d
         ELSE 0
    END                                                                          AS margin_pcent,
    COALESCE(vf.forecast_7d, 0)                                                  AS sell_volume,
    COALESCE(s.sold_7d, 0)::bigint                                               AS sold_7d,
    CASE
        WHEN ls.price IS NULL OR ls.price <= 0     THEN 'flat'
        WHEN pf.forecast_7d > ls.price * 1.05      THEN 'up'
        WHEN pf.forecast_7d > ls.price * 1.001     THEN 'slow_up'
        WHEN pf.forecast_7d < ls.price * 0.95      THEN 'down'
        WHEN pf.forecast_7d < ls.price * 0.999     THEN 'slow_down'
        ELSE 'flat'
    END                                                                          AS tendency,
    b.nb_runs * b.prod_qtt                                                       AS full_batch_raw,
    LEAST(b.nb_runs * b.prod_qtt, COALESCE(vf.forecast_7d, 0))                   AS full_batch_amount,
    LEAST(b.nb_runs * b.prod_qtt, COALESCE(vf.forecast_7d, 0))
        * (pf.forecast_7d * (1.0 - :sell_fee) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit))
                                                                                 AS margin_full_batch
FROM user_industry_costs uic
JOIN blueprints b ON b.id = uic.blueprint_id
JOIN jita_price_forecast_linear_regression pf
    ON pf.type_id = uic.produced_type_id AND pf.forecast_date = CURRENT_DATE + 3
LEFT JOIN jita_volume_forecast_linear_regression vf
    ON vf.type_id = uic.produced_type_id AND vf.forecast_date = CURRENT_DATE + 3
LEFT JOIN (
    SELECT eve_item_id, SUM(volume) AS sold_7d
    FROM sales_finals
    WHERE universe_system_id = 30000142 AND day >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY eve_item_id
) s ON s.eve_item_id = uic.produced_type_id
LEFT JOIN (
    SELECT DISTINCT ON (eve_item_id) eve_item_id, price
    FROM public_trade_orders
    WHERE is_buy_order = FALSE AND universe_system_id = 30000142
    ORDER BY eve_item_id, price ASC
) ls ON ls.eve_item_id = uic.produced_type_id
WHERE uic.user_id    = :user_id
  AND uic.activity_type = 'manufacturing'
  {item_filter}
  AND pf.forecast_7d * (1.0 - :sell_fee) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit) > 0
  AND CASE WHEN pf.forecast_7d > 0
       THEN (pf.forecast_7d * (1.0 - :sell_fee) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit)) / pf.forecast_7d
       ELSE 0 END >= :min_margin_pcent
  AND (b.nb_runs * b.prod_qtt)
      * (pf.forecast_7d * (1.0 - :sell_fee) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit)) >= :min_batch_margin
ORDER BY margin_full_batch DESC
"""


@bp.route('/sell_orders')
@login_required
def show():
    page = request.args.get('page', 1, type=int)
    user = current_user

    sof = user.sell_orders_filtering or {}
    show_selected = sof.get('show_selected_items', False)

    t0 = time.perf_counter()
    if show_selected:
        item_ids = [ei.id for ei in user.eve_items]
        should_run = bool(item_ids)
    else:
        item_ids = None
        should_run = True
    _timings.info('sell_orders.user_items',
                  extra={'duration_ms': (time.perf_counter() - t0) * 1000,
                         'n_items': len(item_ids) if item_ids else -1})

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

        item_filter = 'AND uic.produced_type_id IN :item_ids' if show_selected else ''
        sql = _SQL.format(jita=JITA_SYSTEM_ID, item_filter=item_filter)
        params = {
            'user_id':          user.id,
            'sell_fee':         sell_fee,
            'min_margin_pcent': min_margin_pcent,
            'min_batch_margin': min_batch_margin,
        }

        if show_selected:
            params['item_ids'] = item_ids
            bp_item = bindparam('item_ids', expanding=True)
            count_stmt = text(f'SELECT COUNT(*) FROM ({sql}) t').bindparams(bp_item)
            data_stmt  = text(sql + ' LIMIT :limit OFFSET :offset').bindparams(bp_item)
        else:
            count_stmt = text(f'SELECT COUNT(*) FROM ({sql}) t')
            data_stmt  = text(sql + ' LIMIT :limit OFFSET :offset')

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
    _timings.info('sell_orders.badge_queries',
                  extra={'duration_ms': (time.perf_counter() - t0) * 1000})
    potential_copy_ids        = {r.eve_item_id for r in potential if r.potential_type == 'copy'}
    potential_invent_ids      = {r.eve_item_id for r in potential if r.potential_type == 'invent'}
    potential_copy_invent_ids = {r.eve_item_id for r in potential if r.potential_type == 'copy_invent'}

    in_stock_item_ids = {
        r.eve_item_id for r in
        db.session.query(UserAsset.eve_item_id)
        .filter(UserAsset.user_id == user.id, UserAsset.is_potential == False).all()
    }

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
        'sell_orders/show.html',
        title='Sell orders (mine)',
        sell_orders=rows,
        pagination=pagination,
        owned_bp_ids=owned_bp_ids,
        potential_copy_ids=potential_copy_ids,
        potential_invent_ids=potential_invent_ids,
        potential_copy_invent_ids=potential_copy_invent_ids,
        in_stock_item_ids=in_stock_item_ids,
        sale_order_item_ids=sale_order_item_ids,
        active_job_item_ids=active_job_item_ids,
        copying_item_ids=copying_item_ids,
        inventing_item_ids=inventing_item_ids,
        user=user,
    )
