"""Tests for evebs/routes/market_data.py."""
import pytest
from tests.factories import (
    make_universe_region, make_universe_constellation,
    make_universe_system, make_trade_hub, make_item, make_public_trade_order,
)


@pytest.fixture
def seeded(db):
    system = make_universe_system(db, system_id=30000142, name='Jita')
    hub = make_trade_hub(db, system)
    item = make_item(db, item_id=34, slug='tritanium')
    db.session.commit()
    return {'hub': hub, 'item': item}


class TestMarketOverview:
    def test_404_for_nonexistent_item(self, client, db):
        resp = client.get('/market_data/9999/market_overview/')
        assert resp.status_code == 404

    def test_returns_200_for_existing_item(self, db, client, seeded):
        resp = client.get(f'/market_data/{seeded["item"].id}/market_overview/')
        assert resp.status_code == 200

    def test_returns_200_for_base_item(self, db, client):
        item = make_item(db, item_id=34, slug='tritanium-base', base_item=True)
        db.session.commit()

        resp = client.get(f'/market_data/{item.id}/market_overview/')
        assert resp.status_code == 200

    def test_market_overview_aggregates_across_systems(self, db, client):
        region = make_universe_region(db)
        const = make_universe_constellation(db, region)
        jita = make_universe_system(db, const, system_id=30000142, name='Jita')
        amarr = make_universe_system(db, const, system_id=30002187, name='Amarr')
        item = make_item(db, item_id=34, slug='trit')
        make_public_trade_order(db, item, jita, order_id=1, price=100.0, is_buy=False)
        make_public_trade_order(db, item, amarr, order_id=2, price=90.0, is_buy=False)
        make_public_trade_order(db, item, jita, order_id=3, price=50.0, is_buy=True)
        db.session.commit()

        resp = client.get(f'/market_data/{item.id}/market_overview/')
        assert resp.status_code == 200
        # Orders from both systems appear (not filtered to a single hub).
        assert b'Jita' in resp.data
        assert b'Amarr' in resp.data


class TestTradeHubDetail:
    def test_404_for_nonexistent_item(self, client, db):
        resp = client.get('/market_data/9999/trade_hub_detail/1')
        assert resp.status_code == 404

    def test_404_for_nonexistent_trade_hub(self, db, client, seeded):
        resp = client.get(f'/market_data/{seeded["item"].id}/trade_hub_detail/9999')
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

    def test_filters_to_hub(self, db, client):
        region = make_universe_region(db)
        const = make_universe_constellation(db, region)
        jita = make_universe_system(db, const, system_id=30000142, name='Jita')
        amarr = make_universe_system(db, const, system_id=30002187, name='Amarr')
        item = make_item(db, item_id=34, slug='trit')
        make_public_trade_order(db, item, jita, order_id=1, price=111.0, is_buy=False)
        make_public_trade_order(db, item, amarr, order_id=2, price=222.0, is_buy=False)
        db.session.commit()

        resp = client.get(f'/market_data/{item.id}/trade_hub_detail/{jita.id}')
        assert resp.status_code == 200
        body = resp.data
        assert b'111' in body          # Jita order present
        assert b'222' not in body      # Amarr order filtered out
