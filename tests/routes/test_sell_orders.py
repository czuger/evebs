"""Tests for evebs/routes/sell_orders.py."""
from tests.factories import make_universe_system, make_trade_hub, make_item, make_blueprint


class TestSellOrdersShow:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/sell_orders')
        assert resp.status_code == 302

    def test_returns_200_with_no_blueprints_or_hubs(self, auth_client):
        client, _ = auth_client
        resp = client.get('/sell_orders')
        assert resp.status_code == 200

    def test_returns_200_with_blueprints_and_hubs(self, db, auth_client):
        """SQL query executes when user has both blueprints and trade hubs."""
        client, user = auth_client

        system = make_universe_system(db)
        hub = make_trade_hub(db, system)
        item = make_item(db, item_id=35, slug='ammo-sell', name='Ammo Sell')
        bp = make_blueprint(db, item, manufacturing_cost=100.0)
        user.blueprints.append(bp)
        user.trade_hubs.append(hub)
        db.session.commit()

        resp = client.get('/sell_orders')
        assert resp.status_code == 200
