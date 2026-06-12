"""Tests for the jita_price_spreads view and the /price_spreads page."""
import pytest

from evebs.models import JitaPriceSpread
from tests.factories import make_item, make_jita_min_price, make_jita_price_forecast


def _seed(db, item_id, current, forecast, method='linear'):
    item = make_item(db, item_id=item_id, name=f'Item{item_id}', slug=f'item{item_id}')
    make_jita_min_price(db, item, min_sell_price=current)
    make_jita_price_forecast(db, item, price_forecast_3d=forecast, method=method)
    db.session.commit()
    return item


class TestJitaPriceSpreadView:
    def test_up_hard(self, db):
        _seed(db, 34, current=100.0, forecast=130.0)
        row = db.session.get(JitaPriceSpread, 34)
        assert row.direction == 'up'
        assert row.is_hard is True
        assert abs(row.spread_pcent - 0.30) < 1e-9
        assert abs(row.spread - 30.0) < 1e-9

    def test_up_soft(self, db):
        _seed(db, 34, current=100.0, forecast=105.0)
        row = db.session.get(JitaPriceSpread, 34)
        assert row.direction == 'up'
        assert row.is_hard is False

    def test_flat_below_band(self, db):
        _seed(db, 34, current=100.0, forecast=101.0)
        row = db.session.get(JitaPriceSpread, 34)
        assert row.direction == 'flat'
        assert row.is_hard is False

    def test_down_hard(self, db):
        _seed(db, 34, current=100.0, forecast=70.0)
        row = db.session.get(JitaPriceSpread, 34)
        assert row.direction == 'down'
        assert row.is_hard is True

    def test_min_price_method_is_flat(self, db):
        _seed(db, 34, current=100.0, forecast=130.0, method='min_price')
        row = db.session.get(JitaPriceSpread, 34)
        assert row.direction == 'flat'
        assert row.is_hard is False

    def test_excluded_without_current_price(self, db):
        # forecast but no jita_min_price → no current price → not in the view
        item = make_item(db, item_id=35, name='NoPrice', slug='noprice')
        make_jita_price_forecast(db, item, price_forecast_3d=100.0)
        db.session.commit()
        assert db.session.get(JitaPriceSpread, 35) is None


class TestPriceSpreadsPage:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/price_spreads')
        assert resp.status_code == 302

    def test_returns_200_empty(self, auth_client):
        client, _ = auth_client
        resp = client.get('/price_spreads')
        assert resp.status_code == 200

    def test_lists_item_with_trend_badge(self, db, auth_client):
        client, _ = auth_client
        _seed(db, 34, current=100.0, forecast=130.0)
        resp = client.get('/price_spreads')
        assert resp.status_code == 200
        assert b'Item34' in resp.data
        assert b'Rising hard' in resp.data

    def test_search_filters_by_name(self, db, auth_client):
        client, _ = auth_client
        _seed(db, 34, current=100.0, forecast=130.0)
        _seed(db, 35, current=50.0, forecast=40.0)
        resp = client.get('/price_spreads?q=item35')
        assert resp.status_code == 200
        assert b'Item35' in resp.data
        assert b'Item34' not in resp.data
