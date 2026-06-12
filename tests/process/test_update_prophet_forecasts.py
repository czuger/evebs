"""Tests for process/update_prophet_forecasts.py (the >=90-day Prophet tier)."""
from datetime import date, timedelta

from process.update_prophet_forecasts import update_prophet_forecasts
from evebs.models import JitaPriceForecast
from tests.factories import make_item, make_market_history, make_jita_min_price


def _seed_history(db, item, n_days, start_avg=100.0, slope=1.0):
    today = date.today()
    for i in range(n_days):
        d = today - timedelta(days=n_days - 1 - i)
        make_market_history(db, item, hist_date=d, average=start_avg + slope * i, volume=1000)


class TestUpdateProphetForecasts:
    def test_tiers_with_injected_forecaster(self, db):
        a = make_item(db, item_id=34, name='Prophet', slug='prophet-item')   # >=90 days
        b = make_item(db, item_id=35, name='Linear', slug='linear-item')     # 14-89 days
        c = make_item(db, item_id=36, name='Fallback', slug='fallback-item') # min_price
        _seed_history(db, a, 95)
        _seed_history(db, b, 20)
        make_jita_min_price(db, c, min_sell_price=42.0)
        db.session.commit()

        summary = update_prophet_forecasts(forecaster=lambda ds, ys: 999.0)
        assert summary['eligible'] == 1
        assert summary['fitted'] == 1

        assert db.session.get(JitaPriceForecast, 34).method == 'prophet'
        assert db.session.get(JitaPriceForecast, 34).price_forecast_3d == 999.0
        assert db.session.get(JitaPriceForecast, 35).method == 'linear'
        assert db.session.get(JitaPriceForecast, 36).method == 'min_price'

    def test_failed_fit_keeps_linear_baseline(self, db):
        a = make_item(db, item_id=34, name='Prophet', slug='prophet-item')
        _seed_history(db, a, 95)
        db.session.commit()

        summary = update_prophet_forecasts(forecaster=lambda ds, ys: None)
        assert summary['eligible'] == 1
        assert summary['fitted'] == 0
        # Prophet produced nothing → the linear baseline row is preserved.
        assert db.session.get(JitaPriceForecast, 34).method == 'linear'

    def test_real_prophet_fit(self, db):
        d = make_item(db, item_id=34, name='RealProphet', slug='real-prophet')
        _seed_history(db, d, 100, start_avg=100.0, slope=2.0)  # clean upward trend
        db.session.commit()

        update_prophet_forecasts()   # real Prophet, serial

        row = db.session.get(JitaPriceForecast, 34)
        assert row.method == 'prophet'
        assert row.price_forecast_3d is not None
        assert row.price_forecast_3d > 0
        assert row.price_forecast_3d == row.price_forecast_3d   # not NaN
