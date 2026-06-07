"""Tests for evebs/routes/buy_orders.py."""
import pytest

from tests.factories import (
    make_universe_region, make_universe_constellation,
    make_universe_system, make_trade_hub,
    make_item, make_blueprint, make_jma, make_public_trade_order,
)


@pytest.fixture
def seeded(db, user):
    """Universe + watched item with blueprint, both JMA prices, and a buy order."""
    region = make_universe_region(db)
    constellation = make_universe_constellation(db, region)
    system = make_universe_system(db, constellation, system_id=60_000_001, name='TestHub')
    make_trade_hub(db, system)

    mat  = make_item(db, item_id=34, slug='tritanium', name='Tritanium')
    prod = make_item(db, item_id=35, slug='ammo',      name='Ammo')

    bp = make_blueprint(db, prod, blueprint_id=10035, nb_runs=5, prod_qtt=10)
    bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Tritanium', 'chain': {}}}

    # UserIndustryCost view requires JMA for BOTH the material and the produced item.
    make_jma(db, mat,  min_sell_price=5.0)     # material price → cost computation
    make_jma(db, prod, min_sell_price=2000.0)  # produced item → view JOIN requirement

    from evebs.models.tables.associations import eve_items_users, trade_hubs_users
    db.session.execute(eve_items_users.insert().values(user_id=user.id, eve_item_id=prod.id))
    db.session.execute(trade_hubs_users.insert().values(user_id=user.id, universe_system_id=system.id))

    # Buy order: price=200_000 >> total_cost ≈ 50/unit → batch margin (50 units × ~192k) > 5M default filter
    make_public_trade_order(db, prod, system, order_id=9001, price=200_000.0,
                            is_buy=True, volume_remain=500)

    db.session.commit()
    return {'system': system, 'mat': mat, 'prod': prod, 'bp': bp}


class TestBuyOrders:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/buy_orders')
        assert resp.status_code == 302
        assert 'login' in resp.location.lower() or '/' in resp.location

    def test_returns_200_no_data(self, auth_client):
        client, _ = auth_client
        resp = client.get('/buy_orders')
        assert resp.status_code == 200

    def test_pagination_param_accepted(self, auth_client):
        client, _ = auth_client
        resp = client.get('/buy_orders?page=1')
        assert resp.status_code == 200

    def test_shows_profitable_row(self, db, auth_client, seeded):
        client, _ = auth_client
        resp = client.get('/buy_orders')
        assert resp.status_code == 200
        assert b'Ammo' in resp.data

    def test_shows_all_required_columns(self, db, auth_client, seeded):
        """All 11 column headers must be present."""
        client, _ = auth_client
        resp = client.get('/buy_orders')
        for header in [b'Trade hub', b'Item', b'BP',
                       b'Cost', b'buy', b'Sell tax',
                       b'Margin', b'vol', b'batch']:
            assert header.lower() in resp.data.lower(), f"Missing column header containing {header}"

    def test_item_name_links_to_item_page(self, db, auth_client, seeded):
        client, _ = auth_client
        resp = client.get('/buy_orders')
        assert b'href="/items/ammo"' in resp.data or b'/items/35' in resp.data

    def test_cost_links_to_production_costs(self, db, auth_client, seeded):
        client, _ = auth_client
        resp = client.get('/buy_orders')
        assert b'production_costs' in resp.data

    def test_buy_price_links_to_trade_hub_detail(self, db, auth_client, seeded):
        client, _ = auth_client
        resp = client.get('/buy_orders')
        assert b'trade_hub_detail' in resp.data

    def test_no_row_when_buy_price_below_cost(self, db, auth_client, seeded):
        """Buy order price well below manufacturing cost must not appear."""
        client, _ = auth_client
        from evebs.models import PublicTradeOrder
        PublicTradeOrder.query.filter_by(order_id=9001).update({'price': 1.0})
        db.session.commit()
        resp = client.get('/buy_orders')
        assert resp.status_code == 200
        assert b'Ammo' not in resp.data

    def test_no_row_when_material_has_no_jma_price(self, db, auth_client, seeded):
        """Blueprint whose material lacks a JMA price is excluded by the view."""
        client, _ = auth_client
        from evebs.models import JitaMarketAnalytics
        db.session.delete(db.session.get(JitaMarketAnalytics, 34))
        db.session.commit()
        resp = client.get('/buy_orders')
        assert resp.status_code == 200
        assert b'Ammo' not in resp.data

    def test_no_row_when_user_has_no_hubs(self, db, auth_client, seeded):
        client, user = auth_client
        from evebs.models.tables.associations import trade_hubs_users
        db.session.execute(
            trade_hubs_users.delete().where(trade_hubs_users.c.user_id == user.id)
        )
        db.session.commit()
        resp = client.get('/buy_orders')
        assert resp.status_code == 200
        assert b'Ammo' not in resp.data

    def test_no_row_for_sell_order(self, db, auth_client, seeded):
        """Sell orders must not appear (only buy orders are relevant)."""
        client, _ = auth_client
        from evebs.models import PublicTradeOrder
        PublicTradeOrder.query.filter_by(order_id=9001).update({'is_buy_order': False})
        db.session.commit()
        resp = client.get('/buy_orders')
        assert resp.status_code == 200
        assert b'Ammo' not in resp.data

    def test_highest_buy_order_volume_not_sum(self, db, auth_client, seeded):
        """Buy volume shown is for the single highest-priced order, not the total."""
        client, _ = auth_client
        # Add a second, lower buy order with large volume
        from evebs.models import PublicTradeOrder
        from evebs.models.tables.public_trade_order import PublicTradeOrder as PTO
        from tests.factories import make_public_trade_order
        make_public_trade_order(db, seeded['prod'], seeded['system'],
                                order_id=9002, price=900.0,
                                is_buy=True, volume_remain=9999)
        db.session.commit()

        resp = client.get('/buy_orders')
        assert resp.status_code == 200
        # The highest buy order has volume_remain=500; 9999 (sum) must NOT appear
        assert b'9\xa0999' not in resp.data  # formatted 9 999 with nbsp
        assert b'9999' not in resp.data
