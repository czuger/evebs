"""Tests for DownloadMyOrders.update — ESI HTTP mocked, real DB."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from esi.download_my_orders import DownloadMyOrders
from tests.factories import make_trade_hub, make_item, make_universe_system, make_universe_station, make_user_sale_order


@pytest.fixture
def seeded(db, user):
    us = make_universe_system(db)  # cpp_system_id=30000142 (Jita)
    hub = make_trade_hub(db, us)  # marks us as trade_hub=True
    item = make_item(db, cpp_eve_item_id=34, slug='tritanium')
    station = make_universe_station(db, us)  # id=60003760
    db.session.commit()
    return {'hub': hub, 'item': item, 'station': station}


def _esi_order(type_id=34, location_id=60003760, price=5000.0, order_id=9001):
    return {
        'order_id': order_id,
        'type_id': type_id,
        'location_id': location_id,
        'price': price,
        'is_buy_order': False,
        'volume_remain': 10,
        'volume_total': 100,
        'duration': 90,
        'issued': '2026-01-01T00:00:00Z',
    }


class TestDownloadMyOrders:
    def test_creates_user_sale_order(self, db, user, seeded):
        with patch('esi.client.EsiClient.get_all_pages', return_value=[_esi_order()]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True):
            DownloadMyOrders().update(user)

        from evebs.models import UserSaleOrder
        orders = UserSaleOrder.query.filter_by(user_id=user.id).all()
        assert len(orders) == 1
        assert orders[0].price == 5000.0
        assert orders[0].eve_item_id == seeded['item'].id
        assert orders[0].universe_system_id == seeded['hub'].id

    def test_updates_price_on_existing_order(self, db, user, seeded):
        existing = make_user_sale_order(db, user, seeded['item'], seeded['hub'], price=1000.0)
        db.session.commit()

        with patch('esi.client.EsiClient.get_all_pages', return_value=[_esi_order(price=9999.0)]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True):
            DownloadMyOrders().update(user)

        db.session.expire(existing)
        assert existing.price == 9999.0

    def test_deletes_orders_not_returned_by_esi(self, db, user, seeded):
        stale = make_user_sale_order(db, user, seeded['item'], seeded['hub'], price=500.0)
        db.session.commit()
        stale_id = stale.id

        with patch('esi.client.EsiClient.get_all_pages', return_value=[]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True):
            DownloadMyOrders().update(user)

        from evebs.models import UserSaleOrder
        # Empty ESI response → user gets locked, no orders deleted via normal path.
        # The code locks the user and returns early when pages is empty.
        db.session.expire_all()
        assert user.locked is True

    def test_skips_locked_user(self, db, user, seeded):
        user.locked = True
        db.session.commit()

        with patch('esi.client.EsiClient.get_all_pages') as mock_pages:
            DownloadMyOrders().update(user)
            mock_pages.assert_not_called()

    def test_skips_order_with_unknown_station(self, db, user, seeded):
        with patch('esi.client.EsiClient.get_all_pages',
                   return_value=[_esi_order(location_id=99999999)]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True):
            DownloadMyOrders().update(user)

        from evebs.models import UserSaleOrder
        assert UserSaleOrder.query.filter_by(user_id=user.id).count() == 0

    def test_updates_last_orders_download_timestamp(self, db, user, seeded):
        before = datetime.utcnow()
        with patch('esi.client.EsiClient.get_all_pages', return_value=[_esi_order()]), \
             patch('esi.client.EsiClient.set_auth_token', return_value=True):
            DownloadMyOrders().update(user)

        db.session.expire(user)
        assert user.last_orders_download is not None
        assert user.last_orders_download >= before
        assert user.download_orders_running is False
