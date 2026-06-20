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

# Reaction analog of sell_orders: values each reaction the user can run against the Prophet
# 5-day Jita forecast (market_prophet_forecasts, region The Forge, confidence 0.95, last
# forecast day). reaction cost = material cost + the user's reaction industry taxes
# (user_industry_costs); sell price = forecast avg_predicted; sell fee = price × the user's
# sales_taxes (broker + sales + safety). Batch margin = LEAST(nb_runs×prod_qtt, forecast volume)
# × net margin per unit. Tendency comes from the forecast's price_direction; the price quality
# warning from price_spread_pct. All reactions are shown (not filtered by profitability).
_SQL = """
    SELECT
        ei.id AS item_id, ei.name AS item_name, ei.slug AS item_slug,
        uic.produced_type_id                                  AS eve_item_id,
        uic.blueprint_id                                      AS blueprint_id,
        uic.mat_cost_per_unit + uic.ind_tax_per_unit          AS total_cost_per_unit,
        mpf.avg_predicted                                     AS sell_price,
        mpf.price_spread_pct                                  AS price_spread_pct,
        mpf.price_direction                                   AS price_direction,
        mpf.avg_predicted * :sell_fee                         AS sell_fee_per_unit,
        mpf.avg_predicted * (1.0 - :sell_fee) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit)
                                                              AS margin_per_unit,
        CASE WHEN mpf.avg_predicted > 0
             THEN (mpf.avg_predicted * (1.0 - :sell_fee) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit))
                  / mpf.avg_predicted
             ELSE 0
        END                                                   AS margin_pcent,
        mpf.vol_predicted                                     AS sell_volume,
        COALESCE(s.sold_7d, 0)::bigint                        AS sold_7d,
        b.nb_runs * b.prod_qtt                                AS full_batch_raw,
        LEAST(b.nb_runs * b.prod_qtt, mpf.vol_predicted)      AS full_batch_amount,
        LEAST(b.nb_runs * b.prod_qtt, mpf.vol_predicted)
            * (mpf.avg_predicted * (1.0 - :sell_fee) - (uic.mat_cost_per_unit + uic.ind_tax_per_unit))
                                                              AS margin_full_batch
    FROM user_industry_costs uic
    JOIN blueprints b ON b.id = uic.blueprint_id
    JOIN eve_items ei ON ei.id = uic.produced_type_id
    JOIN (
        SELECT DISTINCT ON (type_id)
               type_id, avg_predicted, vol_predicted, price_spread_pct, price_direction
        FROM market_prophet_forecasts
        WHERE region_id = 10000002 AND confidence = 0.95
        ORDER BY type_id, forecast_date DESC
    ) mpf ON mpf.type_id = uic.produced_type_id
    LEFT JOIN (
        SELECT eve_item_id, SUM(volume) AS sold_7d
        FROM sales_finals
        WHERE universe_system_id = 30000142 AND day >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY eve_item_id
    ) s ON s.eve_item_id = uic.produced_type_id
    WHERE uic.user_id = :user_id
      AND uic.activity_type = 'reaction'
    ORDER BY margin_full_batch DESC
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
                           owned_bp_ids=owned_bp_ids, user=user)


@bp.route('/jita_reactions/refresh', methods=['POST'])
@login_required
def refresh():
    DownloadMyAssets().update(current_user)
    return redirect(url_for('jita_reactions.show'))
