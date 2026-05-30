"""Tests for DownloadPublicTradesOrders.load_from_csv — real DB, temp CSV."""
import csv
import os
import tempfile
from datetime import datetime, timedelta

import pytest

from esi.download_public_orders.upsert import upsert_order
from tests.factories import make_region, make_trade_hub, make_item


def _write_csv(rows, tmp_path):
    path = os.path.join(tmp_path, 'orders.csv')
    fieldnames = ['id', 'volume_remain', 'system_id', 'type_id', 'price',
                  'range', 'volume_total', 'issued', 'duration', 'min_volume', 'is_buy_order']
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    return path


def _order_row(**kwargs):
    defaults = {
        'id': 1001,
        'volume_remain': 100,
        'system_id': 30000142,
        'type_id': 34,
        'price': 5000.0,
        'range': 'station',
        'volume_total': 1000,
        'issued': '2026-01-01T00:00:00',
        'duration': 90,
        'min_volume': 1,
        'is_buy_order': 'false',
    }
    defaults.update(kwargs)
    return defaults


@pytest.fixture
def seeded(db):
    region = make_region(db)
    hub = make_trade_hub(db, region, system_id=30000142)
    item = make_item(db, cpp_eve_item_id=34, slug='tritanium')
    db.session.commit()
    return {'hub': hub, 'item': item}


class TestLoadFromCsv:
    def test_creates_new_order(self, db, seeded, tmp_path):
        path = _write_csv([_order_row()], str(tmp_path))
        DownloadPublicTradesOrders().load_from_csv(path)

        from evebs.models import PublicTradeOrder
        orders = PublicTradeOrder.query.all()
        assert len(orders) == 1
        o = orders[0]
        assert o.order_id == 1001
        assert o.price == 5000.0
        assert o.volume_remain == 100
        assert o.is_buy_order is False
        assert o.trade_hub_id == seeded['hub'].id
        assert o.eve_item_id == seeded['item'].id

    def test_updates_existing_order_price(self, db, seeded, tmp_path):
        from evebs.models import PublicTradeOrder
        existing = PublicTradeOrder(
            order_id=1001,
            trade_hub_id=seeded['hub'].id,
            eve_item_id=seeded['item'].id,
            is_buy_order=False,
            end_time=datetime(2026, 12, 31),
            price=1000.0,
            range='station',
            volume_remain=50,
            volume_total=100,
            min_volume=1,
        )
        db.session.add(existing)
        db.session.commit()

        path = _write_csv([_order_row(price=9999.0)], str(tmp_path))
        DownloadPublicTradesOrders().load_from_csv(path)

        db.session.expire(existing)
        assert existing.price == 9999.0

    def test_skips_zero_volume_rows(self, db, seeded, tmp_path):
        path = _write_csv([_order_row(volume_remain=0)], str(tmp_path))
        DownloadPublicTradesOrders().load_from_csv(path)

        from evebs.models import PublicTradeOrder
        assert PublicTradeOrder.query.count() == 0

    def test_skips_unknown_trade_hub(self, db, seeded, tmp_path):
        path = _write_csv([_order_row(system_id=99999999)], str(tmp_path))
        DownloadPublicTradesOrders().load_from_csv(path)

        from evebs.models import PublicTradeOrder
        assert PublicTradeOrder.query.count() == 0

    def test_skips_unknown_item(self, db, seeded, tmp_path):
        path = _write_csv([_order_row(type_id=99999999)], str(tmp_path))
        DownloadPublicTradesOrders().load_from_csv(path)

        from evebs.models import PublicTradeOrder
        assert PublicTradeOrder.query.count() == 0

    def test_buy_order_flag_parsed(self, db, seeded, tmp_path):
        path = _write_csv([_order_row(is_buy_order='true')], str(tmp_path))
        DownloadPublicTradesOrders().load_from_csv(path)

        from evebs.models import PublicTradeOrder
        assert PublicTradeOrder.query.first().is_buy_order is True

    def test_end_time_computed_from_issued_plus_duration(self, db, seeded, tmp_path):
        path = _write_csv([_order_row(issued='2026-03-01T00:00:00', duration=30)], str(tmp_path))
        DownloadPublicTradesOrders().load_from_csv(path)

        from evebs.models import PublicTradeOrder
        o = PublicTradeOrder.query.first()
        expected = datetime(2026, 3, 1) + timedelta(days=30)
        assert o.end_time == expected

    def test_multiple_orders_committed(self, db, seeded, tmp_path):
        rows = [_order_row(id=1000 + i, system_id=30000142) for i in range(1, 6)]
        # Add a second item for type_id variety
        item2 = make_item(db, cpp_eve_item_id=35, slug='pyerite')
        db.session.commit()
        rows[1]['type_id'] = 35
        rows[2]['type_id'] = 35

        path = _write_csv(rows, str(tmp_path))
        DownloadPublicTradesOrders().load_from_csv(path)

        from evebs.models import PublicTradeOrder
        assert PublicTradeOrder.query.count() == 5
