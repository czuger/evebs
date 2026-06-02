import json
import pytest
from datetime import datetime, timedelta

from tests.factories import make_universe_system, make_trade_hub, make_item


def write_orders_file(tmp_path, orders):
    (tmp_path / 'data').mkdir(exist_ok=True)
    lines = '\n'.join(json.dumps(o) for o in orders)
    (tmp_path / 'data' / 'public_trades_orders.json_stream').write_text(lines + '\n')


def _base_order(**kwargs):
    defaults = {
        'order_id': 1001,
        'system_id': 30000142,
        'type_id': 34,
        'is_buy_order': False,
        'price': 1000.0,
        'volume_remain': 100,
        'volume_total': 100,
        'min_volume': 1,
        'duration': 90,
        'range': 'station',
        'issued': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    defaults.update(kwargs)
    return defaults


@pytest.fixture
def setup(db):
    system = make_universe_system(db, system_id=30000142)
    hub = make_trade_hub(db, system)
    item = make_item(db, item_id=34)
    db.session.commit()
    return hub, item


class TestUpdatePublicOrdersNewOrders:
    def test_creates_new_order(self, db, setup, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        hub, item = setup
        write_orders_file(tmp_path, [_base_order()])
        from process.update_public_orders import run
        run()
        from evebs.models import PublicTradeOrder
        assert PublicTradeOrder.query.count() == 1
        order = PublicTradeOrder.query.one()
        assert order.price == pytest.approx(1000.0)
        assert order.volume_remain == 100

    def test_skips_order_for_unknown_system(self, db, setup, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        write_orders_file(tmp_path, [_base_order(system_id=99999999)])
        from process.update_public_orders import run
        run()
        from evebs.models import PublicTradeOrder
        assert PublicTradeOrder.query.count() == 0

    def test_skips_order_for_unknown_item(self, db, setup, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        write_orders_file(tmp_path, [_base_order(type_id=99999999)])
        from process.update_public_orders import run
        run()
        from evebs.models import PublicTradeOrder
        assert PublicTradeOrder.query.count() == 0

    def test_skips_zero_volume_order(self, db, setup, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        write_orders_file(tmp_path, [_base_order(volume_remain=0)])
        from process.update_public_orders import run
        run()
        from evebs.models import PublicTradeOrder
        assert PublicTradeOrder.query.count() == 0

    def test_noop_when_no_file(self, db, setup, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / 'data').mkdir()
        from process.update_public_orders import run
        run()  # must not raise


class TestUpdatePublicOrdersVolumeChange:
    def test_volume_decrease_creates_sales_final(self, db, setup, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        hub, item = setup
        write_orders_file(tmp_path, [_base_order(volume_remain=100)])
        from process.update_public_orders import run
        run()
        write_orders_file(tmp_path, [_base_order(volume_remain=60)])
        run()
        from evebs.models import SalesFinal
        sf = SalesFinal.query.one()
        assert sf.volume == 40
        assert sf.price == pytest.approx(1000.0)

    def test_no_sale_created_on_price_only_change(self, db, setup, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        hub, item = setup
        write_orders_file(tmp_path, [_base_order(volume_remain=100, price=1000.0)])
        from process.update_public_orders import run
        run()
        write_orders_file(tmp_path, [_base_order(volume_remain=100, price=1200.0)])
        run()
        from evebs.models import SalesFinal
        assert SalesFinal.query.count() == 0


class TestUpdatePublicOrdersExpiry:
    def test_expired_untouched_sell_order_is_deleted_no_sale(self, db, setup, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        hub, item = setup
        write_orders_file(tmp_path, [_base_order(volume_remain=50)])
        from process.update_public_orders import run
        run()
        # Force end_time to the past — order expired, no sale should be recorded
        from evebs.models import PublicTradeOrder
        order = PublicTradeOrder.query.one()
        order.end_time = datetime.utcnow() - timedelta(days=1)
        db.session.commit()
        write_orders_file(tmp_path, [])
        run()
        from evebs.models import SalesFinal
        assert PublicTradeOrder.query.count() == 0
        assert SalesFinal.query.count() == 0

    def test_boughtout_untouched_sell_order_creates_sale(self, db, setup, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        hub, item = setup
        write_orders_file(tmp_path, [_base_order(volume_remain=50)])
        from process.update_public_orders import run
        run()
        # Run with empty file — order within end_time but not returned by ESI = bought out
        write_orders_file(tmp_path, [])
        run()
        from evebs.models import PublicTradeOrder, SalesFinal
        assert PublicTradeOrder.query.count() == 0
        sf = SalesFinal.query.one()
        assert sf.volume == 50
