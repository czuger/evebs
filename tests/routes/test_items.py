"""Tests for evebs/routes/items.py."""
from datetime import date, timedelta

import pytest
from tests.factories import (
    make_universe_system, make_trade_hub, make_item, make_market_group,
    make_blueprint, make_jita_min_price, make_market_history, make_public_trade_order,
)


class TestItemShow:
    def test_404_for_nonexistent_slug(self, client, db):
        resp = client.get('/items/does-not-exist')
        assert resp.status_code == 404

    def test_200_for_existing_slug(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        item = make_item(db, item_id=34, slug='tritanium')
        db.session.commit()

        resp = client.get('/items/tritanium')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data

    def test_item_found_by_numeric_id(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        item = make_item(db, item_id=34, slug='tritanium')
        db.session.commit()

        resp = client.get(f'/items/{item.id}')
        assert resp.status_code == 200


class TestItemManufacturingContext:
    def test_renders_total_cost_without_material_breakdown(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        mat = make_item(db, item_id=34, slug='trit-items', name='Tritanium')
        crafted = make_item(db, item_id=35, slug='ammo-items', name='Ammo Items')
        bp = make_blueprint(db, crafted, prod_qtt=10)
        bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Tritanium', 'chain': {}}}
        make_jita_min_price(db, mat, min_sell_price=50.0)
        db.session.commit()

        resp = client.get('/items/ammo-items')
        assert resp.status_code == 200
        assert b'Ammo Items' in resp.data
        assert b'Production cost' in resp.data
        # The per-material breakdown table is removed.
        assert b'Qty (batch)' not in resp.data

    def test_shows_producing_blueprint(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        crafted = make_item(db, item_id=35, slug='gram-ii', name='Gram II')
        bp = make_blueprint(db, crafted, blueprint_id=77777)
        db.session.commit()

        resp = client.get('/items/gram-ii')
        assert resp.status_code == 200
        assert b'Produced by' in resp.data
        assert b'Gram II Blueprint' in resp.data
        assert b'Type/77777_64.png' in resp.data       # blueprint icon
        assert b'Blueprint type ID' in resp.data
        assert b'77777' in resp.data

    def test_product_keeps_produced_by_when_blueprint_invented(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        crafted = make_item(db, item_id=35, slug='gram-ii', name='Gram II')
        bp = make_blueprint(db, crafted, blueprint_id=77777)
        bp.is_invented_from_id = 12345      # T2 blueprint, invented from a T1 one
        db.session.commit()

        resp = client.get('/items/gram-ii')   # the product page
        assert resp.status_code == 200
        assert b'Produced by' in resp.data
        assert b'Invented by' not in resp.data

    def test_blueprint_item_shows_invented_by(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        product = make_item(db, item_id=35, slug='gram-ii', name='Gram II')
        make_item(db, item_id=1000, slug='gram-i-bp', name='Gram I Blueprint')      # source T1 bp item
        make_item(db, item_id=2000, slug='gram-ii-bp', name='Gram II Blueprint')    # the T2 bp item
        bp = make_blueprint(db, product, blueprint_id=2000)   # Blueprint 2000 produces Gram II
        bp.is_invented_from_id = 1000
        db.session.commit()

        resp = client.get('/items/gram-ii-bp')   # the T2 blueprint's own page
        assert resp.status_code == 200
        assert b'Invented by' in resp.data
        assert b'Gram I Blueprint' in resp.data
        assert b'Type/1000_64.png' in resp.data
        assert b'Produced by' not in resp.data

    def test_market_prices_shown_for_blueprint_with_no_data(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        item = make_item(db, item_id=2000, slug='gram-ii-bp', name='Gram II Blueprint')
        db.session.commit()

        resp = client.get('/items/gram-ii-bp')
        assert resp.status_code == 200
        # All four market price rows show even with no blueprint/manufacturing and no data.
        for label in (b'Jita min sell', b'Jita max buy', b'Universe min sell', b'Universe max buy'):
            assert label in resp.data
        assert b'\xe2\x80\x94' in resp.data   # em dash "—" placeholder for missing data

    def test_universe_prices_link_to_market_overview(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        item = make_item(db, item_id=34, slug='trit')
        make_public_trade_order(db, item, system, order_id=1, price=123.0, is_buy=False)
        db.session.commit()

        resp = client.get('/items/trit')
        assert resp.status_code == 200
        assert b'Universe min sell' in resp.data
        assert b'market_overview' in resp.data

    def test_price_history_chart_rendered(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        item = make_item(db, item_id=34, slug='tritanium', name='Tritanium')
        today = date.today()
        for i in range(5):
            make_market_history(db, item, hist_date=today - timedelta(days=i),
                                region_id=10000002, average=10.0 + i, volume=1000 + i)
        db.session.commit()

        resp = client.get('/items/tritanium')
        assert resp.status_code == 200
        assert b'priceHistoryChart' in resp.data
        assert b'chart.js' in resp.data

    def test_no_chart_without_forge_history(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        item = make_item(db, item_id=34, slug='tritanium', name='Tritanium')
        # History only in another region must not produce a chart.
        make_market_history(db, item, hist_date=date.today(), region_id=10000043)
        db.session.commit()

        resp = client.get('/items/tritanium')
        assert resp.status_code == 200
        assert b'priceHistoryChart' not in resp.data

    def test_reaction_blueprint_with_user_industry_taxes(self, db, auth_client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        mat = make_item(db, item_id=34, slug='full-items', name='Fullerite')
        crafted = make_item(db, item_id=36, slug='c60-items', name='Blue Pill')
        bp = make_blueprint(db, crafted, prod_qtt=1)
        bp.activity_type = 'reaction'
        bp.manufacturing_tree = {'34': {'quantity': 10, 'name': 'Fullerite', 'chain': {}}}
        make_jita_min_price(db, mat, min_sell_price=100.0)
        db.session.commit()

        client, user = auth_client
        user.industry_taxes = {
            'reaction': {'system_cost_index': 5.0, 'scc_tax': 4.0, 'reaction_tax': 2.0}
        }
        db.session.commit()

        resp = client.get('/items/c60-items')
        assert resp.status_code == 200

