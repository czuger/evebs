"""Tests for evebs/routes/market_forecasts.py."""
from datetime import date, timedelta

from evebs.models import MarketProphetForecast, MarketProphetForecastErrors
from tests.factories import make_item, make_market_history

FORGE = 10000002


def _seed_forecast(db, item, vol=1000, confidence=0.95, price_direction=1):
    start = date.today()
    for i in range(5):
        avg = 100.0 + i
        low = 80.0 + i
        high = 120.0 + i
        price_spread = high - low
        db.session.add(MarketProphetForecast(
            region_id=FORGE, type_id=item.id, forecast_date=start + timedelta(days=i + 1),
            confidence=confidence,
            avg_predicted=avg, avg_lower=90.0 + i, avg_upper=110.0 + i,
            low_predicted=low, low_lower=70.0 + i, low_upper=90.0 + i,
            high_predicted=high, high_lower=110.0 + i, high_upper=130.0 + i,
            vol_predicted=float(vol), vol_lower=float(vol - 10), vol_upper=float(vol + 10),
            price_spread=price_spread, price_spread_pct=price_spread / avg,
            price_direction=price_direction))
    db.session.commit()


def _seed_history(db, item, days=5):
    for i in range(days):
        make_market_history(db, item, date.today() - timedelta(days=days - i),
                            region_id=FORGE, average=100.0 + i, lowest=90.0 + i, volume=500)
    db.session.commit()


def _seed_error(db, item, reason='not_enough_history', confidence=0.95):
    db.session.add(MarketProphetForecastErrors(
        region_id=FORGE, type_id=item.id, confidence=confidence, reason=reason))
    db.session.commit()


class TestIndex:
    def test_requires_auth(self, client):
        assert client.get('/market_forecasts').status_code == 302

    def test_lists_item(self, db, auth_client):
        client, _ = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        _seed_forecast(db, item)
        resp = client.get('/market_forecasts')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data
        assert b'/market_forecasts/34' in resp.data
        assert b'Quality' in resp.data
        assert b'Direction' in resp.data
        # Representative row is the LAST forecast day (+5), with an up tendency glyph.
        assert (date.today() + timedelta(days=5)).isoformat().encode() in resp.data
        assert b'&#9650;' in resp.data   # up arrow from shared/_tendency_icon.html

    def test_only_index_confidence(self, db, auth_client):
        client, _ = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        _seed_forecast(db, item, confidence=0.90)   # not the index confidence
        resp = client.get('/market_forecasts')
        assert resp.status_code == 200
        assert b'Tritanium' not in resp.data

    def test_orders_by_volume(self, db, auth_client):
        client, _ = auth_client
        busy = make_item(db, item_id=34, slug='busy', name='BusyItem')
        quiet = make_item(db, item_id=35, slug='quiet', name='QuietItem')
        _seed_forecast(db, busy, vol=9000)
        _seed_forecast(db, quiet, vol=100)
        body = client.get('/market_forecasts').data.decode()
        assert body.index('BusyItem') < body.index('QuietItem')


class TestShow:
    def test_404_for_unknown(self, auth_client):
        client, _ = auth_client
        assert client.get('/market_forecasts/99999').status_code == 404

    def test_renders_charts(self, db, auth_client):
        client, _ = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        _seed_forecast(db, item)
        _seed_history(db, item)
        resp = client.get(f'/market_forecasts/{item.id}')
        assert resp.status_code == 200
        for cid in (b'avgChart', b'lowChart', b'highChart', b'volChart'):
            assert cid in resp.data
        assert b'Prediction quality' in resp.data
        # History overlay + dotted forecast datasets and a Direction column.
        assert b'(history)' in resp.data and b'(forecast)' in resp.data
        assert b'Direction' in resp.data

    def test_error_shows_notice(self, db, auth_client):
        client, _ = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        _seed_error(db, item, reason='not_enough_history')
        resp = client.get(f'/market_forecasts/{item.id}')
        assert resp.status_code == 200
        assert b'not_enough_history' in resp.data
        assert b'avgChart' not in resp.data
