from types import SimpleNamespace

from flask import Blueprint as FlaskBlueprint, render_template, request
from flask_login import login_required
from sqlalchemy import text

from config import PER_PAGE
from evebs.extensions import db
from evebs.models import (
    EveItem, JitaPriceForecastLinearRegression, JitaVolumeForecastLinearRegression,
)
from evebs.utils import SimplePagination

bp = FlaskBlueprint('price_forecasts', __name__)

# One row per item, taken at the +7d horizon (where the two training windows diverge most).
# Each forecast MV trains a 7-day and a 30-day regression; `f7`/`f30` are those windows'
# forecasts for CURRENT_DATE + 7, with |Spread| / |Spread %| (30d vs 7d) and per-window
# confidence. Ordered by smallest spread % first.
_LIST = """
    WITH p AS (
        SELECT type_id,
            MAX(forecast_7d)     FILTER (WHERE forecast_date = CURRENT_DATE + 7) AS f7,
            MAX(forecast_30d)    FILTER (WHERE forecast_date = CURRENT_DATE + 7) AS f30,
            MAX(spread)          FILTER (WHERE forecast_date = CURRENT_DATE + 7) AS spread,
            MAX(spread_percent)  FILTER (WHERE forecast_date = CURRENT_DATE + 7) AS spread_pct,
            MAX(confidence_7d)  AS conf_7d,
            MAX(confidence_30d) AS conf_30d
        FROM jita_price_forecast_linear_regression GROUP BY type_id
    ),
    v AS (
        SELECT type_id,
            MAX(forecast_7d)  FILTER (WHERE forecast_date = CURRENT_DATE + 7) AS f7,
            MAX(forecast_30d) FILTER (WHERE forecast_date = CURRENT_DATE + 7) AS f30,
            MAX(confidence_7d)  AS conf_7d,
            MAX(confidence_30d) AS conf_30d
        FROM jita_volume_forecast_linear_regression GROUP BY type_id
    )
    SELECT
        ei.id AS item_id, ei.name AS item_name, ei.slug AS item_slug,
        p.f7 AS price_7d, p.f30 AS price_30d,
        p.spread AS spread, p.spread_pct AS spread_pct,
        p.conf_7d AS price_conf_7d, p.conf_30d AS price_conf_30d,
        v.f7 AS vol_7d, v.f30 AS vol_30d,
        v.conf_7d AS vol_conf_7d, v.conf_30d AS vol_conf_30d
    FROM p
    JOIN eve_items ei ON ei.id = p.type_id
    LEFT JOIN v ON v.type_id = p.type_id
    {where}
    ORDER BY spread_pct ASC NULLS LAST, ei.name
"""


@bp.route('/price_forecasts')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str).strip()

    where = ''
    params = {}
    if q:
        where = 'WHERE LOWER(ei.name) LIKE :q'
        params['q'] = f'%{q.lower()}%'

    total = db.session.execute(
        text('SELECT COUNT(*) FROM (SELECT DISTINCT p.type_id '
             'FROM jita_price_forecast_linear_regression p '
             'JOIN eve_items ei ON ei.id = p.type_id ' + where + ') t'),
        params,
    ).scalar()

    rows_raw = db.session.execute(
        text(_LIST.format(where=where) + ' LIMIT :limit OFFSET :offset'),
        {**params, 'limit': PER_PAGE, 'offset': (page - 1) * PER_PAGE},
    ).mappings().all()

    rows = [SimpleNamespace(**r) for r in rows_raw]
    pagination = SimplePagination(page, PER_PAGE, total) if total else None
    return render_template('price_forecasts/index.html', rows=rows, pagination=pagination, q=q)


@bp.route('/price_forecasts/<int:item_id>')
@login_required
def show(item_id):
    item = EveItem.query.get_or_404(item_id)
    price_rows = (JitaPriceForecastLinearRegression.query
                  .filter_by(type_id=item_id)
                  .order_by(JitaPriceForecastLinearRegression.forecast_date).all())
    vol_rows = (JitaVolumeForecastLinearRegression.query
                .filter_by(type_id=item_id)
                .order_by(JitaVolumeForecastLinearRegression.forecast_date).all())
    price_series = [{'date': r.forecast_date.isoformat(), 'w7': r.forecast_7d, 'w30': r.forecast_30d}
                    for r in price_rows]
    vol_series = [{'date': r.forecast_date.isoformat(), 'w7': r.forecast_7d, 'w30': r.forecast_30d}
                  for r in vol_rows]
    return render_template('price_forecasts/show.html',
                           item=item,
                           price_rows=price_rows, vol_rows=vol_rows,
                           price_metrics=price_rows[0] if price_rows else None,
                           vol_metrics=vol_rows[0] if vol_rows else None,
                           price_series=price_series, vol_series=vol_series,
                           title=f'Price and volume forecast for {item.name}')
