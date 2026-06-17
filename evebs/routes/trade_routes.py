from types import SimpleNamespace

from flask import Blueprint as FlaskBlueprint, render_template, request, abort
from flask_login import login_required, current_user
from sqlalchemy import text, bindparam

from evebs.extensions import db
from evebs.models import EveItem, TradeRouteBuy
from evebs.utils import SimplePagination
from config import PER_PAGE

bp = FlaskBlueprint('trade_routes', __name__)

# Hardcoded haulage capacity (for now). Profit is computed on the units that fit.
CARGO_M3 = 30_000

# Buy at the source hub's lowest sell price, haul one cargo-hold, then exit at the
# destination either by filling a buy order ('buy') or by placing a sell order ('sell').
_SQL = """
WITH lowest_sell AS (
  SELECT DISTINCT ON (eve_item_id, universe_system_id)
         eve_item_id, universe_system_id, price AS sell_price,
         volume_remain AS sell_volume
  FROM public_trade_orders
  WHERE is_buy_order = FALSE AND universe_system_id IN :hub_ids
  ORDER BY eve_item_id, universe_system_id, price ASC
),
highest_buy AS (
  SELECT DISTINCT ON (eve_item_id, universe_system_id)
         eve_item_id, universe_system_id, price AS buy_price,
         volume_remain AS buy_volume
  FROM public_trade_orders
  WHERE is_buy_order = TRUE AND universe_system_id IN :hub_ids
  ORDER BY eve_item_id, universe_system_id, price DESC
),
daily_sales AS (
  -- average units sold per calendar day at each hub over the last 30 days
  SELECT eve_item_id, universe_system_id,
         floor(SUM(volume) / 30.0) AS daily_volume
  FROM sales_finals
  WHERE universe_system_id IN :hub_ids
    AND day >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY eve_item_id, universe_system_id
),
routes AS (
  -- exit type 'buy': fill a buy order at the destination (instant sale). qty capped by
  -- cargo, the source sell order's volume, the buy order's demand, and the destination's
  -- daily sales (INNER JOIN drops routes with no recorded sales there).
  SELECT src.eve_item_id, ei.name AS item_name, ei.slug AS item_slug,
         src.universe_system_id AS src_hub_id, hb.universe_system_id AS dst_hub_id,
         'buy' AS exit_type, src.sell_price AS buy_price, hb.buy_price AS sell_price,
         ds_d.daily_volume AS daily_sold,
         LEAST(floor(:cargo / ei.volume), src.sell_volume, hb.buy_volume, ds_d.daily_volume) AS qty,
         (hb.buy_price * (1.0 - :sell_tax) - src.sell_price) AS profit_per_unit
  FROM lowest_sell src
  JOIN highest_buy hb ON hb.eve_item_id = src.eve_item_id
                     AND hb.universe_system_id <> src.universe_system_id
  JOIN daily_sales ds_d ON ds_d.eve_item_id = src.eve_item_id
                       AND ds_d.universe_system_id = hb.universe_system_id
  JOIN eve_items ei ON ei.id = src.eve_item_id
  WHERE ei.volume > 0 AND hb.buy_price * (1.0 - :sell_tax) > src.sell_price
  UNION ALL
  -- exit type 'sell': place a sell order at the destination. qty capped by cargo, the
  -- source sell order's available volume, and the destination's daily sales.
  SELECT src.eve_item_id, ei.name, ei.slug,
         src.universe_system_id, ds.universe_system_id,
         'sell', src.sell_price, ds.sell_price,
         ds_d.daily_volume,
         LEAST(floor(:cargo / ei.volume), src.sell_volume, ds_d.daily_volume),
         (ds.sell_price * (1.0 - :sell_fee) - src.sell_price)
  FROM lowest_sell src
  JOIN lowest_sell ds ON ds.eve_item_id = src.eve_item_id
                     AND ds.universe_system_id <> src.universe_system_id
  JOIN daily_sales ds_d ON ds_d.eve_item_id = src.eve_item_id
                       AND ds_d.universe_system_id = ds.universe_system_id
  JOIN eve_items ei ON ei.id = src.eve_item_id
  WHERE ei.volume > 0 AND ds.sell_price * (1.0 - :sell_fee) > src.sell_price
)
SELECT eve_item_id, item_name, item_slug, src_hub_id, dst_hub_id, exit_type,
       buy_price, sell_price, daily_sold, qty, profit_per_unit,
       qty * profit_per_unit AS total_profit
FROM routes
WHERE qty > 0 AND profit_per_unit > 0
  AND (CAST(:src_hub AS INTEGER) IS NULL OR src_hub_id = CAST(:src_hub AS INTEGER))
  AND (CAST(:dst_hub AS INTEGER) IS NULL OR dst_hub_id = CAST(:dst_hub AS INTEGER))
  AND (NOT CAST(:buy_only AS BOOLEAN) OR exit_type = 'buy')
ORDER BY total_profit DESC, eve_item_id
"""


@bp.route('/trade_routes')
@login_required
def show():
    user = current_user
    page = request.args.get('page', 1, type=int)

    sorted_hubs = sorted(user.trade_hubs, key=lambda h: h.name)
    hub_ids = [h.id for h in sorted_hubs]
    hubs = {h.id: h.name for h in sorted_hubs}

    # Optional single-route filter ("<src_id>_<dst_id>"); ignored unless both hubs are
    # the user's own and distinct.
    selected_route = request.args.get('route', '', type=str)
    src_hub = dst_hub = None
    if selected_route:
        parts = selected_route.split('_')
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            s, d = int(parts[0]), int(parts[1])
            if s in hubs and d in hubs and s != d:
                src_hub, dst_hub = s, d
            else:
                selected_route = ''
        else:
            selected_route = ''

    # All ordered hub pairs, for the filter dropdown.
    route_options = [
        {'value': f'{s}_{d}', 'label': f'{hubs[s]} → {hubs[d]}'}
        for s in hub_ids for d in hub_ids if s != d
    ]

    rows = []
    pagination = None
    if len(hub_ids) >= 2:
        st = user.sales_taxes or {}
        sell_tax = (st.get('sales_taxes', 0) + st.get('safety_tax', 0)) / 100.0
        sell_fee = (st.get('broker_fee_taxes', 0) + st.get('sales_taxes', 0)
                    + st.get('safety_tax', 0)) / 100.0
        buy_only = (user.trade_route_filtering or {}).get('buy_orders_only', False)
        params = {'hub_ids': hub_ids, 'cargo': CARGO_M3,
                  'sell_tax': sell_tax, 'sell_fee': sell_fee,
                  'src_hub': src_hub, 'dst_hub': dst_hub,
                  'buy_only': buy_only}
        hub_bind = bindparam('hub_ids', expanding=True)
        count_stmt = text(f'SELECT COUNT(*) FROM ({_SQL}) t').bindparams(hub_bind)
        data_stmt = text(_SQL + ' LIMIT :limit OFFSET :offset').bindparams(hub_bind)

        total = db.session.execute(count_stmt, params).scalar() or 0
        rows_raw = db.session.execute(
            data_stmt, {**params, 'limit': PER_PAGE, 'offset': (page - 1) * PER_PAGE},
        ).mappings().all()
        rows = [SimpleNamespace(**r) for r in rows_raw]
        if total:
            pagination = SimplePagination(page, PER_PAGE, total)

    # Keys of already-saved routes, to pre-check the "Save" checkboxes.
    saved_keys = {(b.eve_item_id, b.src_hub_id, b.dst_hub_id)
                  for b in user.trade_route_buys}

    return render_template('trade_routes/show.html',
                           title='Trade routes',
                           routes=rows,
                           hubs=hubs,
                           hub_count=len(hub_ids),
                           cargo_m3=CARGO_M3,
                           route_options=route_options,
                           selected_route=selected_route,
                           saved_keys=saved_keys,
                           pagination=pagination)


@bp.route('/trade_routes/saved/toggle', methods=['POST'])
@login_required
def save_toggle():
    user = current_user
    item_id = request.form.get('item_id', type=int)
    src_hub_id = request.form.get('src_hub_id', type=int)
    dst_hub_id = request.form.get('dst_hub_id', type=int)
    qty = request.form.get('qty', type=int) or 1
    check_state = request.form.get('check_state') == 'true'

    hub_ids = set(user.trade_hub_ids)
    if (src_hub_id not in hub_ids or dst_hub_id not in hub_ids
            or src_hub_id == dst_hub_id
            or db.session.get(EveItem, item_id) is None):
        abort(404)

    existing = TradeRouteBuy.query.filter_by(
        user_id=user.id, eve_item_id=item_id,
        src_hub_id=src_hub_id, dst_hub_id=dst_hub_id).first()
    if check_state:
        if existing is None:
            db.session.add(TradeRouteBuy(
                user_id=user.id, eve_item_id=item_id,
                src_hub_id=src_hub_id, dst_hub_id=dst_hub_id, quantity=max(1, qty)))
        else:
            existing.quantity = max(1, qty)
    elif existing is not None:
        db.session.delete(existing)
    db.session.commit()
    return ('', 200)


@bp.route('/trade_routes/saved')
@login_required
def saved():
    buys = sorted(current_user.trade_route_buys,
                  key=lambda b: ((b.src_hub.name if b.src_hub else ''),
                                 (b.dst_hub.name if b.dst_hub else ''),
                                 (b.eve_item.name if b.eve_item else '')))
    return render_template('trade_routes/saved.html',
                           title='Trade buy list',
                           buys=buys)


@bp.route('/trade_routes/saved/update', methods=['POST'])
@login_required
def saved_update():
    buy = db.session.get(TradeRouteBuy, request.form.get('id', type=int))
    if buy is None or buy.user_id != current_user.id:
        abort(404)
    buy.quantity = max(1, request.form.get('qty', type=int) or 1)
    db.session.commit()
    return ('', 200)


@bp.route('/trade_routes/saved/delete', methods=['POST'])
@login_required
def saved_delete():
    buy = db.session.get(TradeRouteBuy, request.form.get('id', type=int))
    if buy is None or buy.user_id != current_user.id:
        abort(404)
    db.session.delete(buy)
    db.session.commit()
    return ('', 200)


@bp.route('/trade_routes/saved/delete_all', methods=['POST'])
@login_required
def saved_delete_all():
    TradeRouteBuy.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return ('', 200)
