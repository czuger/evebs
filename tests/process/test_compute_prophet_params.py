"""Tests for process/compute_prophet_params.py."""
from datetime import date, timedelta

from evebs.models import EveItem
from process.compute_prophet_params import compute_prophet_params
from tests.factories import make_item, make_market_history

REGION = 10000002


def _seed_history(db, item, prices, volume=1000, region=REGION):
    """One daily MarketHistory row per price, ending yesterday."""
    n = len(prices)
    start = date.today() - timedelta(days=n)
    for i, price in enumerate(prices):
        make_market_history(db, item, start + timedelta(days=i + 1), region_id=region,
                            average=price, volume=volume)
    db.session.commit()


class TestComputeProphetParams:
    def test_ok_item_gets_full_params(self, db):
        item = make_item(db, item_id=34, slug='trit')
        # 60 days, gentle 1%/day drift → status ok, additive (range < 3), no log transform.
        _seed_history(db, item, [100.0 + i for i in range(60)])

        counts = compute_prophet_params(session=db.session)
        assert counts.get('ok') == 1

        db.session.refresh(item)
        assert item.prophet_ready
        p = item.prophet_params
        assert p['seasonality_mode'] == 'additive'
        assert p['weekly_seasonality'] is True
        assert p['interval_width'] == 0.80
        assert p['n_changepoints'] == 15            # < 180 days
        assert item.prophet_runtime['log_transform'] is False   # range ~1.6 < 5
        assert 0.0 <= item.prophet_reliability <= 100.0

    def test_wide_range_is_multiplicative_and_log_transformed(self, db):
        item = make_item(db, item_id=35, slug='wide')
        # 40 days spanning 100 → 1000 (range ratio 10 > 5) → multiplicative + log transform.
        _seed_history(db, item, [100.0 + 22.5 * i for i in range(40)])

        compute_prophet_params(session=db.session)
        db.session.refresh(item)
        assert item.prophet_params['seasonality_mode'] == 'multiplicative'   # range > 3
        assert item.prophet_params['seasonality_prior_scale'] == 15
        assert item.prophet_runtime['log_transform'] is True                 # range > 5

    def test_flat_price_series_has_no_nan(self, db):
        """A constant price series makes scipy's rvalue NaN — it must be sanitised to 0.0
        (NaN/inf are invalid in Postgres JSON and would break the bulk update)."""
        item = make_item(db, item_id=37, slug='flat')
        _seed_history(db, item, [100.0] * 40)

        counts = compute_prophet_params(session=db.session)
        assert counts.get('ok') == 1
        db.session.refresh(item)
        s = item.prophet_parameters['data_summary']
        assert s['trend_strength'] == 0.0
        assert s['volatility'] == 0.0
        assert s['price_range_ratio'] == 1.0
        assert 0.0 <= s['reliability_score'] <= 100.0

    def test_insufficient_data(self, db):
        item = make_item(db, item_id=36, slug='thin')
        _seed_history(db, item, [100.0 + i for i in range(10)])   # < 30 days

        counts = compute_prophet_params(session=db.session)
        assert counts.get('insufficient_data') == 1
        db.session.refresh(item)
        assert item.prophet_parameters['status'] == 'insufficient_data'
        assert item.prophet_parameters['data_days'] == 10
        assert not item.prophet_ready

    def test_only_eve_items_with_history_touched(self, db):
        with_hist = make_item(db, item_id=34, slug='with-hist')
        no_hist = make_item(db, item_id=99, slug='no-hist')
        _seed_history(db, with_hist, [100.0 + i for i in range(40)])

        compute_prophet_params(session=db.session)
        db.session.refresh(no_hist)
        assert no_hist.prophet_parameters is None   # never analysed
