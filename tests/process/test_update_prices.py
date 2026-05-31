import json
import os
import pytest
from datetime import date, timedelta

from process.update_prices import (
    update_prices_min,
    update_buy_orders_analytics,
    update_weekly_price_details,
    update_market_histories,
)
from tests.factories import (
    make_universe_system, make_trade_hub, make_item, make_blueprint,
    make_public_trade_order, make_sales_final, make_universe_region,
)


@pytest.fixture
def hub_and_item(db):
    system = make_universe_system(db)
    hub = make_trade_hub(db, system)
    item = make_item(db)
    db.session.commit()
    return hub, item


class TestUpdatePricesMin:
    def test_inserts_min_sell_price(self, db, hub_and_item):
        hub, item = hub_and_item
        make_public_trade_order(db, item, hub, order_id=1, price=500.0, is_buy=False)
        make_public_trade_order(db, item, hub, order_id=2, price=300.0, is_buy=False)
        db.session.commit()
        update_prices_min()
        from evebs.models import PricesMin
        pm = PricesMin.query.filter_by(universe_system_id=hub.id, eve_item_id=item.id).one()
        assert pm.min_price == pytest.approx(300.0)

    def test_ignores_buy_orders(self, db, hub_and_item):
        hub, item = hub_and_item
        make_public_trade_order(db, item, hub, order_id=1, price=100.0, is_buy=True)
        db.session.commit()
        update_prices_min()
        from evebs.models import PricesMin
        assert PricesMin.query.count() == 0

    def test_removes_entry_when_sell_orders_gone(self, db, hub_and_item):
        hub, item = hub_and_item
        make_public_trade_order(db, item, hub, order_id=1, price=300.0, is_buy=False)
        db.session.commit()
        update_prices_min()
        from evebs.models import PricesMin
        assert PricesMin.query.count() == 1
        from evebs.models import PublicTradeOrder
        PublicTradeOrder.query.delete()
        db.session.commit()
        update_prices_min()
        assert PricesMin.query.count() == 0

    def test_updates_existing_entry(self, db, hub_and_item):
        hub, item = hub_and_item
        make_public_trade_order(db, item, hub, order_id=1, price=500.0, is_buy=False)
        db.session.commit()
        update_prices_min()
        from evebs.models import PricesMin, PublicTradeOrder
        PublicTradeOrder.query.delete()
        db.session.commit()
        make_public_trade_order(db, item, hub, order_id=2, price=200.0, is_buy=False)
        db.session.commit()
        update_prices_min()
        pm = PricesMin.query.filter_by(universe_system_id=hub.id, eve_item_id=item.id).one()
        assert pm.min_price == pytest.approx(200.0)


class TestUpdateBuyOrdersAnalytics:
    def test_sets_approx_max_price(self, db, hub_and_item):
        hub, item = hub_and_item
        make_public_trade_order(db, item, hub, order_id=1, price=1000.0, is_buy=True)
        make_public_trade_order(db, item, hub, order_id=2, price=800.0, is_buy=True)
        db.session.commit()
        update_buy_orders_analytics()
        from evebs.models import BuyOrdersAnalytic
        boa = BuyOrdersAnalytic.query.filter_by(universe_system_id=hub.id, eve_item_id=item.id).one()
        assert boa.approx_max_price == pytest.approx(900.0)

    def test_noop_when_no_buy_orders(self, db, hub_and_item):
        hub, item = hub_and_item
        make_public_trade_order(db, item, hub, order_id=1, price=500.0, is_buy=False)
        db.session.commit()
        update_buy_orders_analytics()
        from evebs.models import BuyOrdersAnalytic
        assert BuyOrdersAnalytic.query.count() == 0

    def test_fills_single_unit_margin_when_cost_known(self, db, hub_and_item):
        hub, item = hub_and_item
        item.cost = 500.0
        db.session.commit()
        make_public_trade_order(db, item, hub, order_id=1, price=1000.0, is_buy=True, volume_remain=10)
        db.session.commit()
        update_buy_orders_analytics()
        from evebs.models import BuyOrdersAnalytic
        boa = BuyOrdersAnalytic.query.filter_by(universe_system_id=hub.id, eve_item_id=item.id).one()
        assert boa.single_unit_cost == pytest.approx(500.0)
        assert boa.single_unit_margin == pytest.approx(400.0)  # 900 - 500


class TestUpdateWeeklyPriceDetails:
    def test_aggregates_sales_for_today(self, db, hub_and_item):
        hub, item = hub_and_item
        today = date.today()
        make_sales_final(db, item, hub, volume=100, price=500.0, day=today, order_id=1)
        make_sales_final(db, item, hub, volume=200, price=600.0, day=today, order_id=2)
        db.session.commit()
        update_weekly_price_details()
        from evebs.models import WeeklyPriceDetail
        wpd = WeeklyPriceDetail.query.filter_by(
            universe_system_id=hub.id, eve_item_id=item.id, day=today
        ).one()
        assert wpd.volume == 300
        expected_avg = (100 * 500.0 + 200 * 600.0) / 300
        assert wpd.weighted_avg_price == pytest.approx(expected_avg)

    def test_removes_entries_older_than_seven_days(self, db, hub_and_item):
        hub, item = hub_and_item
        old_day = date.today() - timedelta(days=10)
        make_sales_final(db, item, hub, volume=50, price=100.0, day=old_day, order_id=1)
        db.session.commit()
        update_weekly_price_details()
        from evebs.models import WeeklyPriceDetail
        assert WeeklyPriceDetail.query.count() == 0

    def test_updates_weekly_avg_price_on_item_from_jita(self, db):
        system = make_universe_system(db, cpp_system_id=30000142, name='Jita')
        hub = make_trade_hub(db, system)
        item = make_item(db, cpp_eve_item_id=35, slug='rounds')
        today = date.today()
        make_sales_final(db, item, hub, volume=100, price=800.0, day=today, order_id=1)
        db.session.commit()
        update_weekly_price_details()
        db.session.refresh(item)
        assert item.weekly_avg_price == pytest.approx(800.0)

    def test_upserts_existing_entry(self, db, hub_and_item):
        hub, item = hub_and_item
        today = date.today()
        make_sales_final(db, item, hub, volume=100, price=500.0, day=today, order_id=1)
        db.session.commit()
        update_weekly_price_details()
        from evebs.models import WeeklyPriceDetail, SalesFinal
        SalesFinal.query.delete()
        db.session.commit()
        make_sales_final(db, item, hub, volume=50, price=200.0, day=today, order_id=2)
        db.session.commit()
        update_weekly_price_details()
        assert WeeklyPriceDetail.query.count() == 1
        wpd = WeeklyPriceDetail.query.one()
        assert wpd.volume == 50


class TestUpdateMarketHistories:
    def test_inserts_records_from_file(self, db, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / 'data').mkdir()
        region = make_universe_region(db, cpp_region_id=10000002)
        item = make_item(db, cpp_eve_item_id=34)
        db.session.commit()
        record = {
            'cpp_region_id': 10000002,
            'cpp_type_id': 34,
            'volume': 5000,
            'avg': 100.0,
            'max': 120.0,
            'min': 80.0,
        }
        (tmp_path / 'data' / 'regional_sales_volumes.json_stream').write_text(
            json.dumps(record) + '\n'
        )
        update_market_histories()
        from evebs.models import EveMarketHistoriesGroup
        entry = EveMarketHistoriesGroup.query.filter_by(
            eve_item_id=item.id, universe_region_id=region.id
        ).one()
        assert entry.volume == 5000
        assert entry.average == pytest.approx(100.0)

    def test_updates_existing_entry(self, db, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / 'data').mkdir()
        region = make_universe_region(db, cpp_region_id=10000002)
        item = make_item(db, cpp_eve_item_id=34)
        db.session.commit()
        from evebs.models import EveMarketHistoriesGroup
        existing = EveMarketHistoriesGroup(
            eve_item_id=item.id,
            universe_region_id=region.id,
            volume=100,
            average=50.0,
            highest=60.0,
            lowest=40.0,
        )
        db.session.add(existing)
        db.session.commit()
        record = {'cpp_region_id': 10000002, 'cpp_type_id': 34,
                  'volume': 9999, 'avg': 200.0, 'max': 250.0, 'min': 150.0}
        (tmp_path / 'data' / 'regional_sales_volumes.json_stream').write_text(
            json.dumps(record) + '\n'
        )
        update_market_histories()
        db.session.refresh(existing)
        assert existing.volume == 9999
        assert existing.average == pytest.approx(200.0)

    def test_skips_missing_file(self, db, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / 'data').mkdir()
        update_market_histories()  # must not raise

    def test_skips_unknown_region_or_item(self, db, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / 'data').mkdir()
        record = {'cpp_region_id': 99999999, 'cpp_type_id': 99999999,
                  'volume': 1, 'avg': 1.0, 'max': 1.0, 'min': 1.0}
        (tmp_path / 'data' / 'regional_sales_volumes.json_stream').write_text(
            json.dumps(record) + '\n'
        )
        update_market_histories()
        from evebs.models import EveMarketHistoriesGroup
        assert EveMarketHistoriesGroup.query.count() == 0
