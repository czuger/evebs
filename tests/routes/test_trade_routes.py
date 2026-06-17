"""Tests for evebs/routes/trade_routes.py."""
import pytest

from evebs.models.tables.associations import trade_hubs_users
from tests.factories import (
    make_universe_region, make_universe_constellation, make_universe_system,
    make_trade_hub, make_item, make_public_trade_order,
)


def _attach_hub(db, user, system):
    db.session.execute(trade_hubs_users.insert().values(
        user_id=user.id, universe_system_id=system.id))


@pytest.fixture
def hubs(db, user):
    """Two trade hubs (Jita, Amarr) both selected by the user."""
    region = make_universe_region(db)
    const = make_universe_constellation(db, region)
    jita = make_universe_system(db, const, system_id=30000142, name='Jita')
    amarr = make_universe_system(db, const, system_id=30002187, name='Amarr')
    make_trade_hub(db, jita)
    make_trade_hub(db, amarr)
    _attach_hub(db, user, jita)
    _attach_hub(db, user, amarr)
    return {'jita': jita, 'amarr': amarr}


class TestTradeRoutes:
    def test_requires_auth(self, client, db):
        resp = client.get('/trade_routes')
        assert resp.status_code in (301, 302)

    def test_prompt_when_fewer_than_two_hubs(self, auth_client, db):
        client, _user = auth_client
        resp = client.get('/trade_routes')
        assert resp.status_code == 200
        assert b'at least two' in resp.data

    def test_buy_order_exit_route(self, auth_client, db, hubs):
        client, _user = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        item.volume = 10
        # Buy cheap at Jita (sell order), sell into a buy order at Amarr.
        make_public_trade_order(db, item, hubs['jita'], order_id=1, price=100.0, is_buy=False)
        make_public_trade_order(db, item, hubs['amarr'], order_id=2, price=300.0, is_buy=True)
        db.session.commit()

        resp = client.get('/trade_routes')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data
        assert b'Buy order' in resp.data
        assert b'Jita' in resp.data and b'Amarr' in resp.data

    def test_sell_order_exit_route(self, auth_client, db, hubs):
        client, _user = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        item.volume = 10
        # Buy cheap at Jita, place a sell order at Amarr (higher sell price there).
        make_public_trade_order(db, item, hubs['jita'], order_id=1, price=100.0, is_buy=False)
        make_public_trade_order(db, item, hubs['amarr'], order_id=2, price=400.0, is_buy=False)
        db.session.commit()

        resp = client.get('/trade_routes')
        assert resp.status_code == 200
        assert b'Sell order' in resp.data

    def test_no_route_when_unprofitable(self, auth_client, db, hubs):
        client, _user = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        item.volume = 10
        # Destination buy price below source sell price → no profit.
        make_public_trade_order(db, item, hubs['jita'], order_id=1, price=100.0, is_buy=False)
        make_public_trade_order(db, item, hubs['amarr'], order_id=2, price=50.0, is_buy=True)
        db.session.commit()

        resp = client.get('/trade_routes')
        assert resp.status_code == 200
        assert b'No profitable trade routes.' in resp.data

    def test_buy_exit_qty_capped_by_demand_volume(self, auth_client, db, hubs):
        client, _user = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        item.volume = 1   # cargo alone would allow 30000 units
        # Source sell order has 7 units; destination buy order wants only 4.
        make_public_trade_order(db, item, hubs['jita'], order_id=1, price=100.0,
                                is_buy=False, volume_remain=7)
        make_public_trade_order(db, item, hubs['amarr'], order_id=2, price=300.0,
                                is_buy=True, volume_remain=4)
        db.session.commit()

        client.get('/trade_routes')   # exercise the endpoint
        row = self._run_sql(db)
        assert row['exit_type'] == 'buy'
        assert row['qty'] == 4   # min(30000, 7, 4)
        assert row['total_profit'] == pytest.approx(row['qty'] * row['profit_per_unit'])

    def test_sell_exit_qty_capped_by_source_volume(self, auth_client, db, hubs):
        client, _user = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        item.volume = 1
        # Only a sell-order exit exists; source has 6 units available at the buy price.
        make_public_trade_order(db, item, hubs['jita'], order_id=1, price=100.0,
                                is_buy=False, volume_remain=6)
        make_public_trade_order(db, item, hubs['amarr'], order_id=2, price=400.0,
                                is_buy=False, volume_remain=999)
        db.session.commit()

        client.get('/trade_routes')
        row = self._run_sql(db)
        assert row['exit_type'] == 'sell'
        assert row['qty'] == 6   # min(30000, 6)

    def test_route_filter_limits_to_one_pair(self, auth_client, db, hubs):
        client, _user = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        item.volume = 10
        # Profitable both directions: cheap at Jita / dear buy at Amarr, and vice-versa.
        make_public_trade_order(db, item, hubs['jita'], order_id=1, price=100.0, is_buy=False)
        make_public_trade_order(db, item, hubs['amarr'], order_id=2, price=300.0, is_buy=True)
        make_public_trade_order(db, item, hubs['amarr'], order_id=3, price=100.0, is_buy=False)
        make_public_trade_order(db, item, hubs['jita'], order_id=4, price=300.0, is_buy=True)
        db.session.commit()

        # Unfiltered: both directions produce a profitable buy-order row.
        all_body = client.get('/trade_routes').data.decode()
        assert all_body.count('class="badge') == 2

        # Filter to Jita -> Amarr only: dropdown offers it and the table is scoped to one row.
        resp = client.get(f"/trade_routes?route={hubs['jita'].id}_{hubs['amarr'].id}")
        assert resp.status_code == 200
        body = resp.data.decode()
        assert 'Jita → Amarr' in body          # dropdown option rendered
        assert body.count('class="badge') == 1  # only the single selected route

        # Bad/foreign route value falls back to all routes (no crash).
        resp = client.get('/trade_routes?route=999_888')
        assert resp.status_code == 200
        assert resp.data.decode().count('class="badge') == 2

    @staticmethod
    def _run_sql(db):
        """Run the route's query for the default-tax user and return the single row."""
        from sqlalchemy import bindparam, text
        from evebs.routes.trade_routes import _SQL, CARGO_M3
        stmt = text(_SQL).bindparams(bindparam('hub_ids', expanding=True))
        return db.session.execute(stmt, {
            'hub_ids': [30000142, 30002187],
            'cargo': CARGO_M3, 'sell_tax': 0.04, 'sell_fee': 0.06,
            'src_hub': None, 'dst_hub': None,
        }).mappings().first()

    def test_ordered_by_total_profit(self, auth_client, db, hubs):
        client, _user = auth_client
        low = make_item(db, item_id=34, slug='low', name='LowProfit')
        low.volume = 10
        high = make_item(db, item_id=35, slug='high', name='HighProfit')
        high.volume = 10
        make_public_trade_order(db, low, hubs['jita'], order_id=1, price=100.0, is_buy=False)
        make_public_trade_order(db, low, hubs['amarr'], order_id=2, price=150.0, is_buy=True)
        make_public_trade_order(db, high, hubs['jita'], order_id=3, price=100.0, is_buy=False)
        make_public_trade_order(db, high, hubs['amarr'], order_id=4, price=1000.0, is_buy=True)
        db.session.commit()

        resp = client.get('/trade_routes')
        assert resp.status_code == 200
        body = resp.data.decode()
        assert body.index('HighProfit') < body.index('LowProfit')
