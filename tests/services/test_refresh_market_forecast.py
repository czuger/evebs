"""Tests for process/refresh_market_forecast.py.

A deterministic `forecaster` is injected so the suite never runs Prophet."""
from datetime import date, timedelta

import pytest

from evebs.models import MarketProphetForecast, MarketProphetForecastErrors
from process.refresh_market_forecast import (
    generate_forecast, run_all, recompute_price_directions, _price_direction, FORECAST_DAYS,
)
from tests.factories import make_item, make_market_history

REGION = 10000002


def fake_fit(ds, y, periods, width):
    """Return `periods` deterministic (yhat, lower, upper) tuples off the last value."""
    base = float(y[-1])
    return [(base + i, base + i - 1.0, base + i + 1.0) for i in range(periods)]


def _seed(db, item, n, region=REGION, volume=1000):
    start = date.today() - timedelta(days=n + 1)
    for i in range(n):
        make_market_history(db, item, start + timedelta(days=i + 1), region_id=region,
                            average=100.0 + i, lowest=90.0 + i, volume=volume)
    db.session.commit()


class TestGenerateForecast:
    def test_not_enough_history_records_error(self, db):
        item = make_item(db, item_id=34, slug='trit')
        _seed(db, item, 10)   # < 30 rows
        result = generate_forecast(REGION, item.id, forecaster=fake_fit)
        assert result == {"status": "error", "reason": "not_enough_history"}
        # An error row is written; no forecast rows.
        err = MarketProphetForecastErrors.query.filter_by(region_id=REGION, type_id=item.id).one()
        assert err.reason == 'not_enough_history'
        assert MarketProphetForecast.query.filter_by(region_id=REGION, type_id=item.id).count() == 0

    def test_forecast_clears_prior_error(self, db):
        item = make_item(db, item_id=34, slug='trit')
        db.session.add(MarketProphetForecastErrors(
            region_id=REGION, type_id=item.id, confidence=0.95, reason='not_enough_history'))
        db.session.commit()
        _seed(db, item, 40)
        generate_forecast(REGION, item.id, forecaster=fake_fit)
        assert MarketProphetForecast.query.filter_by(region_id=REGION, type_id=item.id).count() == FORECAST_DAYS
        assert MarketProphetForecastErrors.query.filter_by(region_id=REGION, type_id=item.id).count() == 0

    def test_generates_five_rows(self, db):
        item = make_item(db, item_id=34, slug='trit')
        _seed(db, item, 40)
        result = generate_forecast(REGION, item.id, forecaster=fake_fit)
        assert result == {"status": "ok", "inserted": FORECAST_DAYS}

        rows = (MarketProphetForecast.query
                .filter_by(region_id=REGION, type_id=item.id)
                .order_by(MarketProphetForecast.forecast_date).all())
        assert len(rows) == FORECAST_DAYS
        last_hist = date.today() - timedelta(days=1)
        assert [r.forecast_date for r in rows] == [
            last_hist + timedelta(days=i) for i in range(1, FORECAST_DAYS + 1)]
        first = rows[0]
        assert first.confidence == 0.95
        assert first.avg_predicted is not None and first.low_predicted is not None
        assert first.high_predicted is not None
        # Volume is forecast (rows have volume > 0) and rounded to an integer value.
        assert first.vol_predicted is not None
        assert first.vol_predicted == float(round(first.vol_predicted))
        # Price spread is computed and non-null.
        assert first.price_spread == pytest.approx(first.high_predicted - first.low_predicted)
        assert first.price_spread_pct == pytest.approx(first.price_spread / first.avg_predicted)
        # fake_fit's first prediction equals the last seeded average → flat (0).
        assert first.price_direction == 0

    def test_regenerate_replaces_existing(self, db):
        item = make_item(db, item_id=34, slug='trit')
        _seed(db, item, 40)
        generate_forecast(REGION, item.id, forecaster=fake_fit)
        generate_forecast(REGION, item.id, forecaster=fake_fit)
        assert MarketProphetForecast.query.filter_by(
            region_id=REGION, type_id=item.id).count() == FORECAST_DAYS

    def test_custom_confidence_stored(self, db):
        item = make_item(db, item_id=34, slug='trit')
        _seed(db, item, 40)
        generate_forecast(REGION, item.id, confidence=0.8, forecaster=fake_fit)
        assert MarketProphetForecast.query.first().confidence == 0.8


class TestPriceDirection:
    def test_encoding(self):
        assert _price_direction(None, 100) is None
        assert _price_direction(100, None) is None
        assert _price_direction(100, 0) is None
        assert _price_direction(100, 100) == 0       # flat
        assert _price_direction(100, 106) == 1       # > +5% → up
        assert _price_direction(100, 100.5) == 2     # > +0.1% → slow_up
        assert _price_direction(100, 94) == -1       # < -5% → down
        assert _price_direction(100, 99.5) == -2     # < -0.1% → slow_down


class TestRecomputePriceDirections:
    def test_corrects_stored_direction(self, db):
        item = make_item(db, item_id=34, slug='trit')
        # Last market-history average = 100.
        make_market_history(db, item, date.today(), region_id=REGION,
                            average=100.0, lowest=95.0, volume=500)
        # Forecast rows predict 110 (well above 100 → 'up') but carry a wrong code.
        for i in range(FORECAST_DAYS):
            db.session.add(MarketProphetForecast(
                region_id=REGION, type_id=item.id, confidence=0.95,
                forecast_date=date.today() + timedelta(days=i + 1),
                avg_predicted=110.0, avg_lower=105.0, avg_upper=115.0,
                low_predicted=100.0, low_lower=95.0, low_upper=105.0,
                high_predicted=120.0, high_lower=115.0, high_upper=125.0,
                vol_predicted=500.0, vol_lower=490.0, vol_upper=510.0,
                price_spread=20.0, price_spread_pct=20.0 / 110.0, price_direction=-1))
        db.session.commit()

        n = recompute_price_directions(region_id=REGION)
        assert n == FORECAST_DAYS
        rows = MarketProphetForecast.query.filter_by(region_id=REGION, type_id=item.id).all()
        assert all(r.price_direction == 1 for r in rows)   # 110 > 100 * 1.05 → up


class TestRunAll:
    def test_processes_every_item(self, db):
        ok_item = make_item(db, item_id=34, slug='ok-item')
        thin_item = make_item(db, item_id=35, slug='thin-item')
        _seed(db, ok_item, 40)          # enough history → forecast
        _seed(db, thin_item, 5)         # too little → status marker

        counts = run_all(region_id=REGION, forecaster=fake_fit)
        assert counts == {'ok': 1, 'error': 1}
        assert MarketProphetForecast.query.filter_by(type_id=ok_item.id).count() == FORECAST_DAYS
        assert MarketProphetForecastErrors.query.filter_by(
            type_id=thin_item.id).one().reason == 'not_enough_history'

    def test_limit(self, db):
        a = make_item(db, item_id=34, slug='a-item')
        make_item(db, item_id=35, slug='b-item')
        _seed(db, a, 40)
        db.session.commit()
        counts = run_all(region_id=REGION, forecaster=fake_fit, limit=1)
        assert sum(counts.values()) == 1
