"""Tests for evebs/routes/market_data.py."""
import pytest
from tests.factories import make_region, make_trade_hub, make_item, make_public_trade_order


@pytest.fixture
def seeded(db):
    region = make_region(db)
    hub = make_trade_hub(db, region, system_id=30000142, name='Jita')
    item = make_item(db, cpp_eve_item_id=34, slug='tritanium')
    db.session.commit()
    return {'hub': hub, 'item': item}


class TestMarketOverview:
    def test_404_for_nonexistent_item(self, client, db):
        resp = client.get('/market_data/9999/market_overview/')
        assert resp.status_code == 404

    def test_returns_200_for_existing_item(self, db, client, seeded):
        resp = client.get(f'/market_data/{seeded["item"].id}/market_overview/')
        assert resp.status_code == 200

    def test_base_item_uses_prices_min(self, db, client):
        region = make_region(db)
        hub = make_trade_hub(db, region)
        item = make_item(db, cpp_eve_item_id=34, slug='tritanium-base', base_item=True)
        db.session.commit()

        resp = client.get(f'/market_data/{item.id}/market_overview/')
        assert resp.status_code == 200


class TestTradeHubDetail:
    def test_404_for_nonexistent_item(self, client, db):
        resp = client.get('/market_data/9999/trade_hub_detail/1')
        assert resp.status_code == 404

    def test_returns_200_for_existing_item_and_hub(self, db, client, seeded):
        resp = client.get(
            f'/market_data/{seeded["item"].id}/trade_hub_detail/{seeded["hub"].id}'
        )
        assert resp.status_code == 200

    def test_shows_sell_orders(self, db, client, seeded):
        make_public_trade_order(db, seeded['item'], seeded['hub'],
                                order_id=1001, price=5000.0, is_buy=False)
        db.session.commit()

        resp = client.get(
            f'/market_data/{seeded["item"].id}/trade_hub_detail/{seeded["hub"].id}'
        )
        assert resp.status_code == 200
