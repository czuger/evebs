"""Tests for evebs/routes/trade_routes.py."""
from datetime import date

import pytest

from evebs.models import TradeRouteBuy
from evebs.models.tables.associations import trade_hubs_users
from tests.factories import (
    make_universe_region, make_universe_constellation, make_universe_system,
    make_trade_hub, make_item, make_public_trade_order, make_sales_final,
)


def _attach_hub(db, user, system):
    db.session.execute(trade_hubs_users.insert().values(
        user_id=user.id, universe_system_id=system.id))


def _seed_daily(db, item, hub, volume=30000):
    """Seed recorded sales at a hub. daily_volume = floor(volume / 30); the default
    30000 → 1000/day, well above the other caps so it doesn't bind unless intended."""
    make_sales_final(db, item, hub, volume=volume, day=date.today(),
                     order_id=item.id * 100 + hub.id % 97)


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
        _seed_daily(db, item, hubs['amarr'])
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
        _seed_daily(db, item, hubs['amarr'])
        db.session.commit()

        resp = client.get('/trade_routes')
        assert resp.status_code == 200
        assert b'Sell order' in resp.data

    def test_buy_orders_only_filter_hides_sell_exit(self, auth_client, db, hubs):
        client, user = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        item.volume = 10
        # Only a sell-order exit exists (no buy order at the destination).
        make_public_trade_order(db, item, hubs['jita'], order_id=1, price=100.0, is_buy=False)
        make_public_trade_order(db, item, hubs['amarr'], order_id=2, price=400.0, is_buy=False)
        _seed_daily(db, item, hubs['amarr'])
        db.session.commit()

        # Off → the sell-order route shows.
        assert b'Sell order' in client.get('/trade_routes').data

        # On → no rows (only buy-order exits would survive).
        user.trade_route_filtering = {'buy_orders_only': True}
        db.session.commit()
        resp = client.get('/trade_routes')
        assert resp.status_code == 200
        assert b'No profitable trade routes.' in resp.data

    def test_buy_orders_only_keeps_buy_exit(self, auth_client, db, hubs):
        client, user = auth_client
        user.trade_route_filtering = {'buy_orders_only': True}
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        item.volume = 10
        make_public_trade_order(db, item, hubs['jita'], order_id=1, price=100.0, is_buy=False)
        make_public_trade_order(db, item, hubs['amarr'], order_id=2, price=300.0, is_buy=True)
        _seed_daily(db, item, hubs['amarr'])
        db.session.commit()

        resp = client.get('/trade_routes')
        assert resp.status_code == 200
        assert b'Buy order' in resp.data

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
        _seed_daily(db, item, hubs['amarr'])   # daily 1000, does not bind
        db.session.commit()

        client.get('/trade_routes')   # exercise the endpoint
        row = self._run_sql(db)
        assert row['exit_type'] == 'buy'
        assert row['qty'] == 4   # min(30000, 7, 4, 1000)
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
        _seed_daily(db, item, hubs['amarr'])   # daily 1000, does not bind
        db.session.commit()

        client.get('/trade_routes')
        row = self._run_sql(db)
        assert row['exit_type'] == 'sell'
        assert row['qty'] == 6   # min(30000, 6, 1000)

    def test_route_filter_limits_to_one_pair(self, auth_client, db, hubs):
        client, _user = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        item.volume = 10
        # Profitable both directions: cheap at Jita / dear buy at Amarr, and vice-versa.
        make_public_trade_order(db, item, hubs['jita'], order_id=1, price=100.0, is_buy=False)
        make_public_trade_order(db, item, hubs['amarr'], order_id=2, price=300.0, is_buy=True)
        make_public_trade_order(db, item, hubs['amarr'], order_id=3, price=100.0, is_buy=False)
        make_public_trade_order(db, item, hubs['jita'], order_id=4, price=300.0, is_buy=True)
        _seed_daily(db, item, hubs['amarr'])   # destination for Jita → Amarr
        _seed_daily(db, item, hubs['jita'])    # destination for Amarr → Jita
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

    def test_qty_capped_by_destination_daily_sales(self, auth_client, db, hubs):
        client, _user = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        item.volume = 1
        # Cargo (30000) and order volumes are large; the destination only sells ~3/day.
        make_public_trade_order(db, item, hubs['jita'], order_id=1, price=100.0,
                                is_buy=False, volume_remain=9999)
        make_public_trade_order(db, item, hubs['amarr'], order_id=2, price=300.0,
                                is_buy=True, volume_remain=9999)
        _seed_daily(db, item, hubs['amarr'], volume=90)   # floor(90/30) = 3
        db.session.commit()

        client.get('/trade_routes')
        row = self._run_sql(db)
        assert row['exit_type'] == 'buy'
        assert row['daily_sold'] == 3
        assert row['qty'] == 3   # min(30000, 9999, 9999, 3)
        assert row['total_profit'] == pytest.approx(row['qty'] * row['profit_per_unit'])

    def test_route_dropped_when_no_destination_sales(self, auth_client, db, hubs):
        client, _user = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        item.volume = 10
        # Profitable spread but no recorded sales at the destination → route dropped.
        make_public_trade_order(db, item, hubs['jita'], order_id=1, price=100.0, is_buy=False)
        make_public_trade_order(db, item, hubs['amarr'], order_id=2, price=300.0, is_buy=True)
        db.session.commit()

        resp = client.get('/trade_routes')
        assert resp.status_code == 200
        assert b'No profitable trade routes.' in resp.data

    @staticmethod
    def _run_sql(db):
        """Run the route's query for the default-tax user and return the single row."""
        from sqlalchemy import bindparam, text
        from evebs.routes.trade_routes import _SQL, CARGO_M3
        stmt = text(_SQL).bindparams(bindparam('hub_ids', expanding=True))
        return db.session.execute(stmt, {
            'hub_ids': [30000142, 30002187],
            'cargo': CARGO_M3, 'sell_tax': 0.04, 'sell_fee': 0.06,
            'src_hub': None, 'dst_hub': None, 'buy_only': False,
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
        _seed_daily(db, low, hubs['amarr'])
        _seed_daily(db, high, hubs['amarr'])
        db.session.commit()

        resp = client.get('/trade_routes')
        assert resp.status_code == 200
        body = resp.data.decode()
        assert body.index('HighProfit') < body.index('LowProfit')


class TestSavedBuys:
    def _item(self, db):
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        db.session.commit()
        return item

    def test_toggle_requires_auth(self, client, db):
        resp = client.post('/trade_routes/saved/toggle', data={'item_id': 1})
        assert resp.status_code in (301, 302)

    def test_toggle_on_creates_then_off_removes(self, auth_client, db, hubs):
        client, user = auth_client
        item = self._item(db)
        data = {'item_id': item.id, 'src_hub_id': hubs['jita'].id,
                'dst_hub_id': hubs['amarr'].id, 'qty': 5, 'check_state': 'true'}
        assert client.post('/trade_routes/saved/toggle', data=data).status_code == 200
        row = TradeRouteBuy.query.filter_by(user_id=user.id).one()
        assert (row.eve_item_id, row.src_hub_id, row.dst_hub_id) == (item.id, hubs['jita'].id, hubs['amarr'].id)
        assert row.quantity == 5

        off = {**data, 'check_state': 'false'}
        assert client.post('/trade_routes/saved/toggle', data=off).status_code == 200
        assert TradeRouteBuy.query.filter_by(user_id=user.id).count() == 0

    def test_toggle_clamps_quantity_to_one(self, auth_client, db, hubs):
        client, user = auth_client
        item = self._item(db)
        client.post('/trade_routes/saved/toggle', data={
            'item_id': item.id, 'src_hub_id': hubs['jita'].id,
            'dst_hub_id': hubs['amarr'].id, 'qty': 0, 'check_state': 'true'})
        assert TradeRouteBuy.query.filter_by(user_id=user.id).one().quantity == 1

    def test_toggle_updates_existing_without_duplicate(self, auth_client, db, hubs):
        client, user = auth_client
        item = self._item(db)
        base = {'item_id': item.id, 'src_hub_id': hubs['jita'].id,
                'dst_hub_id': hubs['amarr'].id, 'check_state': 'true'}
        client.post('/trade_routes/saved/toggle', data={**base, 'qty': 5})
        client.post('/trade_routes/saved/toggle', data={**base, 'qty': 12})
        rows = TradeRouteBuy.query.filter_by(user_id=user.id).all()
        assert len(rows) == 1 and rows[0].quantity == 12

    def test_toggle_rejects_non_user_hub(self, auth_client, db, hubs):
        client, _user = auth_client
        item = self._item(db)
        other = make_universe_system(db, system_id=30002053, name='Hek')
        make_trade_hub(db, other)   # a hub, but not one the user selected
        db.session.commit()
        resp = client.post('/trade_routes/saved/toggle', data={
            'item_id': item.id, 'src_hub_id': other.id,
            'dst_hub_id': hubs['amarr'].id, 'qty': 3, 'check_state': 'true'})
        assert resp.status_code == 404

    def test_route_table_prechecks_saved(self, auth_client, db, hubs):
        client, user = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        item.volume = 10
        make_public_trade_order(db, item, hubs['jita'], order_id=1, price=100.0, is_buy=False)
        make_public_trade_order(db, item, hubs['amarr'], order_id=2, price=300.0, is_buy=True)
        _seed_daily(db, item, hubs['amarr'])
        db.session.add(TradeRouteBuy(user_id=user.id, eve_item_id=item.id,
                                     src_hub_id=hubs['jita'].id, dst_hub_id=hubs['amarr'].id,
                                     quantity=3))
        db.session.commit()

        body = client.get('/trade_routes').data.decode()
        assert 'save-route' in body
        assert 'checked' in body

    def test_saved_screen_lists_and_edits(self, auth_client, db, hubs):
        client, user = auth_client
        item = self._item(db)
        buy = TradeRouteBuy(user_id=user.id, eve_item_id=item.id,
                            src_hub_id=hubs['jita'].id, dst_hub_id=hubs['amarr'].id, quantity=4)
        db.session.add(buy)
        db.session.commit()

        resp = client.get('/trade_routes/saved')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data
        # EVE paste export: "ItemName<TAB>quantity".
        assert b'Show as text (EVE paste)' in resp.data
        assert b'Tritanium\t4' in resp.data

        assert client.post('/trade_routes/saved/update',
                           data={'id': buy.id, 'qty': 9}).status_code == 200
        db.session.refresh(buy)
        assert buy.quantity == 9

        assert client.post('/trade_routes/saved/update',
                           data={'id': buy.id, 'qty': 0}).status_code == 200
        db.session.refresh(buy)
        assert buy.quantity == 1   # clamped

        assert client.post('/trade_routes/saved/delete',
                           data={'id': buy.id}).status_code == 200
        assert db.session.get(TradeRouteBuy, buy.id) is None

    def test_saved_delete_all(self, auth_client, db, hubs, admin_user):
        client, user = auth_client
        item = self._item(db)
        db.session.add(TradeRouteBuy(user_id=user.id, eve_item_id=item.id,
                                     src_hub_id=hubs['jita'].id, dst_hub_id=hubs['amarr'].id, quantity=4))
        db.session.add(TradeRouteBuy(user_id=user.id, eve_item_id=item.id,
                                     src_hub_id=hubs['amarr'].id, dst_hub_id=hubs['jita'].id, quantity=2))
        # Another user's row must survive.
        db.session.add(TradeRouteBuy(user_id=admin_user.id, eve_item_id=item.id,
                                     src_hub_id=hubs['jita'].id, dst_hub_id=hubs['amarr'].id, quantity=7))
        db.session.commit()

        assert client.post('/trade_routes/saved/delete_all').status_code == 200
        assert TradeRouteBuy.query.filter_by(user_id=user.id).count() == 0
        assert TradeRouteBuy.query.filter_by(user_id=admin_user.id).count() == 1

    def test_saved_update_delete_reject_other_user(self, auth_client, db, hubs, admin_user):
        client, _user = auth_client
        item = self._item(db)
        foreign = TradeRouteBuy(user_id=admin_user.id, eve_item_id=item.id,
                                src_hub_id=hubs['jita'].id, dst_hub_id=hubs['amarr'].id, quantity=4)
        db.session.add(foreign)
        db.session.commit()

        assert client.post('/trade_routes/saved/update',
                           data={'id': foreign.id, 'qty': 9}).status_code == 404
        assert client.post('/trade_routes/saved/delete',
                           data={'id': foreign.id}).status_code == 404
