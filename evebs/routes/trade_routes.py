from types import SimpleNamespace

from flask import Blueprint as FlaskBlueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import text, bindparam

from evebs.extensions import db
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
routes AS (
  -- exit type 'buy': fill a buy order at the destination (instant sale).
  -- qty capped by cargo, the source sell order's volume, and the buy order's demand.
  SELECT src.eve_item_id, ei.name AS item_name, ei.slug AS item_slug,
         src.universe_system_id AS src_hub_id, hb.universe_system_id AS dst_hub_id,
         'buy' AS exit_type, src.sell_price AS buy_price, hb.buy_price AS sell_price,
         LEAST(floor(:cargo / ei.volume), src.sell_volume, hb.buy_volume) AS qty,
         (hb.buy_price * (1.0 - :sell_tax) - src.sell_price) AS profit_per_unit
  FROM lowest_sell src
  JOIN highest_buy hb ON hb.eve_item_id = src.eve_item_id
                     AND hb.universe_system_id <> src.universe_system_id
  JOIN eve_items ei ON ei.id = src.eve_item_id
  WHERE ei.volume > 0 AND hb.buy_price * (1.0 - :sell_tax) > src.sell_price
  UNION ALL
  -- exit type 'sell': place a sell order at the destination.
  -- qty capped by cargo and the source sell order's available volume.
  SELECT src.eve_item_id, ei.name, ei.slug,
         src.universe_system_id, ds.universe_system_id,
         'sell', src.sell_price, ds.sell_price,
         LEAST(floor(:cargo / ei.volume), src.sell_volume),
         (ds.sell_price * (1.0 - :sell_fee) - src.sell_price)
  FROM lowest_sell src
  JOIN lowest_sell ds ON ds.eve_item_id = src.eve_item_id
                     AND ds.universe_system_id <> src.universe_system_id
  JOIN eve_items ei ON ei.id = src.eve_item_id
  WHERE ei.volume > 0 AND ds.sell_price * (1.0 - :sell_fee) > src.sell_price
)
SELECT eve_item_id, item_name, item_slug, src_hub_id, dst_hub_id, exit_type,
       buy_price, sell_price, qty, profit_per_unit,
       qty * profit_per_unit AS total_profit
FROM routes
WHERE qty > 0 AND profit_per_unit > 0
  AND (CAST(:src_hub AS INTEGER) IS NULL OR src_hub_id = CAST(:src_hub AS INTEGER))
  AND (CAST(:dst_hub AS INTEGER) IS NULL OR dst_hub_id = CAST(:dst_hub AS INTEGER))
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
        params = {'hub_ids': hub_ids, 'cargo': CARGO_M3,
                  'sell_tax': sell_tax, 'sell_fee': sell_fee,
                  'src_hub': src_hub, 'dst_hub': dst_hub}
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

    return render_template('trade_routes/show.html',
                           title='Trade routes',
                           routes=rows,
                           hubs=hubs,
                           hub_count=len(hub_ids),
                           cargo_m3=CARGO_M3,
                           route_options=route_options,
                           selected_route=selected_route,
                           pagination=pagination)
