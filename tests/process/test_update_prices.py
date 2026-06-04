import pytest
from datetime import date, timedelta

from process.update_prices import (
    update_buy_orders_analytics,
    update_weekly_price_details,
)
from tests.factories import (
    make_universe_system, make_trade_hub, make_item, make_blueprint,
    make_public_trade_order, make_sales_final,
)


@pytest.fixture
def hub_and_item(db):
    system = make_universe_system(db)
    hub = make_trade_hub(db, system)
    item = make_item(db)
    db.session.commit()
    return hub, item


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

    def test_fills_single_unit_margin_from_blueprint(self, db, hub_and_item):
        hub, item = hub_and_item
        make_blueprint(db, item, prod_qtt=1, manufacturing_cost=500.0)
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
