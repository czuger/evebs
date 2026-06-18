from types import SimpleNamespace

from flask import Blueprint as FlaskBlueprint, render_template, request, abort
from flask_login import login_required
from sqlalchemy import text

from config import PER_PAGE
from evebs.extensions import db
from evebs.models import (
    EveItem, MarketHistory, MarketProphetForecast, MarketProphetForecastErrors,
)
from evebs.utils import SimplePagination

bp = FlaskBlueprint('market_forecasts', __name__)

FORGE_REGION_ID = 10000002   # The Forge (Jita) — only region forecast for now.
INDEX_CONFIDENCE = 0.95      # the only confidence level computed/shown

# One row per item: its last forecast day (DISTINCT ON latest forecast_date) at the
# index confidence, joined to eve_items. Ordered by predicted volume desc.
_LIST = """
    WITH last_day AS (
        SELECT DISTINCT ON (type_id)
               type_id, forecast_date,
               avg_predicted, low_predicted, high_predicted, vol_predicted,
               price_spread_pct, price_direction
        FROM market_prophet_forecasts
        WHERE region_id = :region AND confidence = :confidence
        ORDER BY type_id, forecast_date DESC
    )
    SELECT ei.id AS item_id, ei.name AS item_name, ei.slug AS item_slug,
           n.forecast_date,
           n.avg_predicted, n.low_predicted, n.high_predicted, n.vol_predicted,
           n.price_spread_pct, n.price_direction
    FROM last_day n
    JOIN eve_items ei ON ei.id = n.type_id
    {where}
    ORDER BY n.vol_predicted DESC NULLS LAST, ei.name
"""


@bp.route('/market_forecasts')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str).strip()

    params = {'region': FORGE_REGION_ID, 'confidence': INDEX_CONFIDENCE}
    where = ''
    if q:
        where = 'WHERE LOWER(ei.name) LIKE :q'
        params['q'] = f'%{q.lower()}%'

    total = db.session.execute(
        text('SELECT COUNT(*) FROM (SELECT DISTINCT mpf.type_id '
             'FROM market_prophet_forecasts mpf JOIN eve_items ei ON ei.id = mpf.type_id '
             'WHERE mpf.region_id = :region AND mpf.confidence = :confidence '
             + ('AND LOWER(ei.name) LIKE :q ' if q else '') + ') t'),
        params,
    ).scalar()

    rows_raw = db.session.execute(
        text(_LIST.format(where=where) + ' LIMIT :limit OFFSET :offset'),
        {**params, 'limit': PER_PAGE, 'offset': (page - 1) * PER_PAGE},
    ).mappings().all()

    rows = [SimpleNamespace(**r) for r in rows_raw]
    pagination = SimplePagination(page, PER_PAGE, total) if total else None
    return render_template('market_forecasts/index.html',
                           rows=rows, pagination=pagination, q=q,
                           title='Market forecasts')


@bp.route('/market_forecasts/<int:type_id>')
@login_required
def show(type_id):
    item = EveItem.query.get(type_id)
    forecast_rows = (MarketProphetForecast.query
                     .filter_by(region_id=FORGE_REGION_ID, type_id=type_id, confidence=INDEX_CONFIDENCE)
                     .order_by(MarketProphetForecast.forecast_date).all())

    error = None
    if not forecast_rows:
        error = (MarketProphetForecastErrors.query
                 .filter_by(region_id=FORGE_REGION_ID, type_id=type_id, confidence=INDEX_CONFIDENCE)
                 .first())
        if error is None:
            abort(404)

    avg_series = [{'date': r.forecast_date.isoformat(), 'p': r.avg_predicted,
                   'lo': r.avg_lower, 'hi': r.avg_upper} for r in forecast_rows]
    low_series = [{'date': r.forecast_date.isoformat(), 'p': r.low_predicted,
                   'lo': r.low_lower, 'hi': r.low_upper} for r in forecast_rows]
    high_series = [{'date': r.forecast_date.isoformat(), 'p': r.high_predicted,
                    'lo': r.high_lower, 'hi': r.high_upper} for r in forecast_rows]
    vol_series = [{'date': r.forecast_date.isoformat(), 'p': r.vol_predicted,
                   'lo': r.vol_lower, 'hi': r.vol_upper} for r in forecast_rows]

    # Last 5 days of actual market history (oldest → newest) to overlay on the charts.
    hist = (MarketHistory.query
            .filter_by(region_id=FORGE_REGION_ID, type_id=type_id)
            .order_by(MarketHistory.date.desc()).limit(5).all())[::-1]
    hist_avg = [{'date': h.date.isoformat(), 'v': h.average} for h in hist]
    hist_low = [{'date': h.date.isoformat(), 'v': h.lowest} for h in hist]
    hist_high = [{'date': h.date.isoformat(), 'v': h.highest} for h in hist]
    hist_vol = [{'date': h.date.isoformat(), 'v': h.volume} for h in hist]

    return render_template('market_forecasts/show.html',
                           item=item, type_id=type_id,
                           meta=forecast_rows[0] if forecast_rows else None,
                           forecast_rows=forecast_rows,
                           avg_series=avg_series, low_series=low_series,
                           high_series=high_series, vol_series=vol_series,
                           hist_avg=hist_avg, hist_low=hist_low,
                           hist_high=hist_high, hist_vol=hist_vol,
                           has_forecast=bool(forecast_rows),
                           error=error,
                           confidence=INDEX_CONFIDENCE,
                           quality_pct=forecast_rows[0].price_spread_pct if forecast_rows else None,
                           title=f'Market forecast for {item.name if item else type_id}')
