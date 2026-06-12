"""Tests for process/update_price_forecasts.py — the tiered 3-day forecast table."""
from datetime import date, timedelta

from process.update_price_forecasts import update_price_forecasts, FORGE_REGION_ID
from evebs.models import JitaPriceForecast
from tests.factories import make_item, make_market_history, make_jita_min_price

_EPOCH = date(1970, 1, 1)


def _epoch_days(d):
    return (d - _EPOCH).days


class TestUpdatePriceForecasts:
    def test_linear_tier_extrapolates_trend(self, db):
        """An item with >=14 days of Forge history gets a linear forecast at +3 days."""
        item = make_item(db, item_id=34, name='Tritanium', slug='tritanium')
        a, b = 1000.0, 5.0   # average = a + b * epoch_day  (perfectly linear)
        today = date.today()
        for i in range(14):
            d = today - timedelta(days=13 - i)
            make_market_history(db, item, hist_date=d, region_id=FORGE_REGION_ID,
                                average=a + b * _epoch_days(d), volume=1000)
        db.session.commit()

        summary = update_price_forecasts()
        assert summary['linear'] == 1

        row = db.session.get(JitaPriceForecast, 34)
        assert row is not None
        assert row.method == 'linear'
        expected = a + b * (_epoch_days(today) + 3)
        assert abs(row.price_forecast_3d - expected) < expected * 1e-3
        # increasing series → +3 day forecast exceeds the last observed average
        assert row.price_forecast_3d > a + b * _epoch_days(today)

    def test_min_price_fallback_when_too_few_days(self, db):
        """An item with no usable Forge history falls back to jita_min_prices."""
        item = make_item(db, item_id=35, name='Pyerite', slug='pyerite')
        make_jita_min_price(db, item, min_sell_price=42.0)
        db.session.commit()

        update_price_forecasts()

        row = db.session.get(JitaPriceForecast, 35)
        assert row is not None
        assert row.method == 'min_price'
        assert row.price_forecast_3d == 42.0

    def test_item_with_neither_is_excluded(self, db):
        make_item(db, item_id=36, name='Mexallon', slug='mexallon')
        db.session.commit()

        update_price_forecasts()

        assert db.session.get(JitaPriceForecast, 36) is None

    def test_non_forge_history_is_ignored(self, db):
        """History outside The Forge must not produce a (linear) forecast."""
        item = make_item(db, item_id=37, name='Isogen', slug='isogen')
        today = date.today()
        for i in range(14):
            d = today - timedelta(days=13 - i)
            make_market_history(db, item, hist_date=d, region_id=10000043,  # Domain
                                average=1000.0 + i, volume=1000)
        db.session.commit()

        update_price_forecasts()

        assert db.session.get(JitaPriceForecast, 37) is None
