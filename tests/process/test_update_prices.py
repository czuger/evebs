import pytest
from datetime import date

from process.update_prices import update_buy_orders_analytics
from tests.factories import (
    make_universe_system, make_trade_hub, make_item, make_blueprint,
    make_public_trade_order,
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
