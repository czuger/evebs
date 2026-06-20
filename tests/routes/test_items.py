"""Tests for evebs/routes/items.py."""
from datetime import date, timedelta

import pytest
from tests.factories import (
    make_universe_system, make_trade_hub, make_item, make_market_group,
    make_blueprint, make_jita_min_price, make_market_history, make_public_trade_order,
    make_user_asset,
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

    def test_reaction_product_produced_by_formula(self, db, client):
        """A reaction product shows 'Produced by <Reaction Formula>' with the formula type id."""
        product = make_item(db, item_id=16679, slug='fullerides', name='Fullerides')
        make_item(db, item_id=46209, slug='fullerides-reaction-formula',
                  name='Fullerides Reaction Formula')
        bp = make_blueprint(db, product, blueprint_id=46209)
        bp.activity_type = 'reaction'
        db.session.commit()

        resp = client.get('/items/fullerides')
        assert resp.status_code == 200
        assert b'Produced by' in resp.data
        assert b'Fullerides Reaction Formula' in resp.data
        assert b'Type/46209_64.png' in resp.data       # formula blueprint icon
        assert b'46209' in resp.data                   # blueprint type id

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

    def test_material_modifications_link_for_manufacturing_item(self, db, auth_client):
        client, _user = auth_client
        system = make_universe_system(db)
        make_trade_hub(db, system)
        item = make_item(db, item_id=34, slug='trit')
        bp = make_blueprint(db, item)
        bp.activity_type = 'manufacturing'
        db.session.commit()

        resp = client.get('/items/trit')
        assert resp.status_code == 200
        assert b'blueprint_modifications' in resp.data

    def test_no_material_modifications_link_for_t2_item(self, db, auth_client):
        client, _user = auth_client
        system = make_universe_system(db)
        make_trade_hub(db, system)
        item = make_item(db, item_id=34, slug='trit')
        bp = make_blueprint(db, item)
        bp.activity_type = 'manufacturing'
        bp.is_invented_from_id = 35   # T2: invented from a T1 blueprint
        db.session.commit()

        resp = client.get('/items/trit')
        assert resp.status_code == 200
        assert b'blueprint_modifications' not in resp.data

    def test_no_material_modifications_link_for_non_manufacturing_item(self, db, auth_client):
        client, _user = auth_client
        system = make_universe_system(db)
        make_trade_hub(db, system)
        item = make_item(db, item_id=34, slug='trit')   # raw material, no blueprint
        db.session.commit()

        resp = client.get('/items/trit')
        assert resp.status_code == 200
        assert b'blueprint_modifications' not in resp.data

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


class TestItemReciprocity:
    def test_shows_products_using_item_as_material(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        mat = make_item(db, item_id=34, slug='trit', name='Tritanium')
        prod = make_item(db, item_id=35, slug='ammo', name='Ammo')
        bp = make_blueprint(db, prod)
        bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Tritanium', 'chain': {}}}
        db.session.commit()

        resp = client.get('/items/trit')
        assert resp.status_code == 200
        assert b'is involved in production of' in resp.data
        assert b'href="/items/ammo"' in resp.data

    def test_nested_only_material_not_listed(self, db, client):
        """An item used only deep in the nested chain (not a direct material) is not listed."""
        system = make_universe_system(db)
        make_trade_hub(db, system)
        deep = make_item(db, item_id=34, slug='trit', name='Tritanium')
        prod = make_item(db, item_id=35, slug='ammo', name='Ammo')
        bp = make_blueprint(db, prod)
        bp.manufacturing_tree = {
            '99': {'quantity': 5, 'name': 'Intermediate',
                   'chain': {'34': {'quantity': 100, 'name': 'Tritanium', 'chain': {}}}},
        }
        db.session.commit()

        resp = client.get('/items/trit')
        assert resp.status_code == 200
        assert b'is involved in production of' not in resp.data

    def test_shows_t2_blueprints_invented_from_item(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        t1_bp = make_item(db, item_id=1000, slug='gram-i-bp', name='Gram I Blueprint')
        t2_bp = make_item(db, item_id=2000, slug='gram-ii-bp', name='Gram II Blueprint')
        product = make_item(db, item_id=35, slug='gram-ii', name='Gram II')
        bp = make_blueprint(db, product, blueprint_id=2000)   # Blueprint 2000 produces Gram II
        bp.is_invented_from_id = 1000
        db.session.commit()

        resp = client.get('/items/gram-i-bp')   # the T1 blueprint's page
        assert resp.status_code == 200
        assert b'is involved in invention of' in resp.data
        assert b'href="/items/gram-ii-bp"' in resp.data

    def test_plain_item_shows_neither_row(self, db, client):
        system = make_universe_system(db)
        make_trade_hub(db, system)
        make_item(db, item_id=34, slug='trit', name='Tritanium')
        db.session.commit()

        resp = client.get('/items/trit')
        assert resp.status_code == 200
        assert b'is involved in production of' not in resp.data
        assert b'is involved in invention of' not in resp.data


class TestItemOwnership:
    def test_card_hidden_when_logged_out(self, db, client):
        make_item(db, item_id=34, slug='trit', name='Tritanium')
        db.session.commit()

        resp = client.get('/items/trit')
        assert resp.status_code == 200
        assert b'Your ownership' not in resp.data

    def test_asset_owned_shows_yes(self, db, auth_client):
        client, user = auth_client
        item = make_item(db, item_id=34, slug='trit', name='Tritanium')
        make_user_asset(db, user, item, quantity=1200)
        db.session.commit()

        resp = client.get('/items/trit')
        assert resp.status_code == 200
        assert b'Your ownership' in resp.data
        assert b'In assets' in resp.data
        assert b'<span class="badge bg-success">Yes</span>' in resp.data

    def test_asset_not_owned_shows_no(self, db, auth_client):
        client, user = auth_client
        make_item(db, item_id=34, slug='trit', name='Tritanium')
        db.session.commit()

        resp = client.get('/items/trit')
        assert resp.status_code == 200
        assert b'In assets' in resp.data
        assert b'<span class="badge bg-secondary">No</span>' in resp.data

    def test_blueprint_owned_shows_line(self, db, auth_client):
        client, user = auth_client
        item = make_item(db, item_id=35, slug='ammo', name='Ammo')
        bp = make_blueprint(db, item)
        user.blueprints.append(bp)
        db.session.commit()

        resp = client.get('/items/ammo')
        assert resp.status_code == 200
        assert b'Blueprint owned' in resp.data

    def test_blueprint_not_owned_hides_line(self, db, auth_client):
        client, user = auth_client
        item = make_item(db, item_id=35, slug='ammo', name='Ammo')
        make_blueprint(db, item)
        db.session.commit()

        resp = client.get('/items/ammo')
        assert resp.status_code == 200
        assert b'Blueprint owned' not in resp.data

    def test_invention_blueprint_owned_shows_line(self, db, auth_client):
        client, user = auth_client
        t1_product = make_item(db, item_id=1000, slug='gram-i', name='Gram I')
        t1_bp = make_blueprint(db, t1_product, blueprint_id=1000)
        product = make_item(db, item_id=35, slug='gram-ii', name='Gram II')
        t2_bp = make_blueprint(db, product, blueprint_id=2000)
        t2_bp.is_invented_from_id = t1_bp.id
        user.blueprints.append(t1_bp)
        db.session.commit()

        resp = client.get('/items/gram-ii')
        assert resp.status_code == 200
        assert b'Invention blueprint owned' in resp.data



class TestItemSearch:
    def test_redirects_unauthenticated(self, client):
        assert client.get('/items/search').status_code == 302

    def test_empty_query_renders_form(self, db, auth_client):
        client, _ = auth_client
        resp = client.get('/items/search')
        assert resp.status_code == 200
        assert b'Search items' in resp.data

    def test_space_becomes_wildcard(self, db, auth_client):
        """'trit ium' should match 'Tritanium' (each space -> SQL %)."""
        client, _ = auth_client
        make_item(db, item_id=34, slug='tritanium', name='Tritanium')
        make_item(db, item_id=35, slug='pyerite', name='Pyerite')
        db.session.commit()

        resp = client.get('/items/search?q=trit+ium')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data
        assert b'Pyerite' not in resp.data
        assert b'/items/tritanium' in resp.data

    def test_no_match_message(self, db, auth_client):
        client, _ = auth_client
        make_item(db, item_id=34, slug='tritanium', name='Tritanium')
        db.session.commit()

        resp = client.get('/items/search?q=zzz')
        assert resp.status_code == 200
        assert b'No items match' in resp.data


class TestLastViewedItems:
    def test_redirects_unauthenticated(self, client):
        assert client.get('/items/last_viewed').status_code == 302

    def test_show_records_view_for_authed_user(self, db, auth_client):
        from evebs.models import LastViewedItem
        client, user = auth_client
        make_item(db, item_id=34, slug='tritanium', name='Tritanium')
        db.session.commit()

        client.get('/items/tritanium')
        rows = LastViewedItem.query.filter_by(user_id=user.id).all()
        assert len(rows) == 1
        assert rows[0].eve_item_id == 34

    def test_revisit_bumps_without_duplicating(self, db, auth_client):
        from evebs.models import LastViewedItem
        client, user = auth_client
        make_item(db, item_id=34, slug='tritanium', name='Tritanium')
        db.session.commit()

        client.get('/items/tritanium')
        client.get('/items/tritanium')
        assert LastViewedItem.query.filter_by(user_id=user.id).count() == 1

    def test_anonymous_show_records_nothing(self, db, client):
        from evebs.models import LastViewedItem
        make_item(db, item_id=34, slug='tritanium', name='Tritanium')
        db.session.commit()

        client.get('/items/tritanium')
        assert LastViewedItem.query.count() == 0

    def test_view_count_increments_on_each_view(self, db, auth_client):
        from evebs.models import LastViewedItem
        client, user = auth_client
        make_item(db, item_id=34, slug='tritanium', name='Tritanium')
        db.session.commit()

        client.get('/items/tritanium')
        client.get('/items/tritanium')
        client.get('/items/tritanium')
        row = LastViewedItem.query.filter_by(user_id=user.id, eve_item_id=34).one()
        assert row.view_count == 3

    def test_no_item_limit(self, db, auth_client):
        from evebs.models import LastViewedItem
        client, user = auth_client
        for i in range(25):
            make_item(db, item_id=100 + i, slug=f'item-{i}', name=f'Item {i}')
        db.session.commit()

        for i in range(25):
            client.get(f'/items/item-{i}')

        assert LastViewedItem.query.filter_by(user_id=user.id).count() == 25

    def test_listing_orders_by_view_count_desc(self, db, auth_client):
        client, user = auth_client
        make_item(db, item_id=34, slug='tritanium', name='Tritanium')
        make_item(db, item_id=35, slug='pyerite', name='Pyerite')
        db.session.commit()

        client.get('/items/tritanium')          # 1 view
        client.get('/items/pyerite')            # 2 views
        client.get('/items/pyerite')

        resp = client.get('/items/last_viewed')
        assert resp.status_code == 200
        body = resp.data
        assert body.index(b'Pyerite') < body.index(b'Tritanium')
