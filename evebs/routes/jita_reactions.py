from types import SimpleNamespace

from flask import Blueprint as FlaskBlueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import text

from config import PER_PAGE
from esi.download_my_assets import DownloadMyAssets
from evebs.extensions import db
from evebs.utils import SimplePagination

bp = FlaskBlueprint('jita_reactions', __name__)

JITA_SYSTEM_ID = 30000142

# Per-item: reaction cost = material cost + the user's reaction industry taxes
# (user_industry_costs); est. sell price = the lowest live Jita sell order (read straight from
# public_trade_orders, like buy_orders); sell tax = est. price × the user's sales_taxes
# (broker + sales + safety). Benefit is per batch: prod_qtt × (net sell price − reaction cost).
_SQL = """
    WITH lowest_sell AS (
        SELECT DISTINCT ON (eve_item_id)
            eve_item_id,
            price AS sell_price
        FROM public_trade_orders
        WHERE is_buy_order = FALSE
          AND universe_system_id = 30000142
        ORDER BY eve_item_id, price ASC
    )
    SELECT
        ei.id AS item_id, ei.name AS item_name, ei.slug AS item_slug,
        uic.blueprint_id AS blueprint_id,
        COALESCE(mg.name, '') AS market_group_name,
        uic.mat_cost_per_unit + uic.ind_tax_per_unit          AS reaction_cost,
        ls.sell_price                                         AS estimated_selling_price,
        ls.sell_price * :sell_fee                             AS selling_tax,
        b.prod_qtt * (ls.sell_price * (1.0 - :sell_fee)
                      - (uic.mat_cost_per_unit + uic.ind_tax_per_unit)) AS benefit
    FROM user_industry_costs uic
    JOIN blueprints b ON b.id = uic.blueprint_id
    JOIN eve_items ei ON ei.id = uic.produced_type_id
    LEFT JOIN market_groups mg ON mg.id = ei.market_group_id
    JOIN lowest_sell ls ON ls.eve_item_id = uic.produced_type_id
    WHERE uic.user_id = :user_id
      AND uic.activity_type = 'reaction'
    ORDER BY benefit DESC
"""


@bp.route('/jita_reactions')
@login_required
def show():
    page = request.args.get('page', 1, type=int)
    user = current_user

    st = user.sales_taxes or {}
    sell_fee = (
        st.get('broker_fee_taxes', 0)
        + st.get('sales_taxes', 0)
        + st.get('safety_tax', 0)
    ) / 100.0

    params = {'user_id': user.id, 'sell_fee': sell_fee}

    total = db.session.execute(text(f'SELECT COUNT(*) FROM ({_SQL}) t'), params).scalar()

    rows_raw = db.session.execute(
        text(_SQL + ' LIMIT :limit OFFSET :offset'),
        {**params, 'limit': PER_PAGE, 'offset': (page - 1) * PER_PAGE},
    ).mappings().all()

    rows = [SimpleNamespace(**r) for r in rows_raw]
    pagination = SimplePagination(page, PER_PAGE, total) if total else None
    owned_bp_ids = {b.id for b in user.blueprints}

    return render_template('jita_reactions/show.html', rows=rows, pagination=pagination,
                           owned_bp_ids=owned_bp_ids)


@bp.route('/jita_reactions/refresh', methods=['POST'])
@login_required
def refresh():
    DownloadMyAssets().update(current_user)
    return redirect(url_for('jita_reactions.show'))
