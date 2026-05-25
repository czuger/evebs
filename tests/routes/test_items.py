"""Tests for evebs/routes/items.py."""
import pytest
from tests.factories import make_region, make_trade_hub, make_item, make_market_group


class TestItemShow:
    def test_404_for_nonexistent_slug(self, client, db):
        resp = client.get('/items/does-not-exist')
        assert resp.status_code == 404

    def test_200_for_existing_slug(self, db, client):
        region = make_region(db)
        make_trade_hub(db, region, system_id=30000142)
        item = make_item(db, cpp_eve_item_id=34, slug='tritanium')
        db.session.commit()

        resp = client.get('/items/tritanium')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data

    def test_item_found_by_numeric_id(self, db, client):
        region = make_region(db)
        make_trade_hub(db, region, system_id=30000142)
        item = make_item(db, cpp_eve_item_id=34, slug='tritanium')
        db.session.commit()

        resp = client.get(f'/items/{item.id}')
        assert resp.status_code == 200

    def test_taxes_default_when_constant_missing(self, db, client):
        region = make_region(db)
        make_trade_hub(db, region, system_id=30000142)
        make_item(db, cpp_eve_item_id=34, slug='tritanium')
        db.session.commit()

        # No Constant row seeded — route should fall back to 1.13
        resp = client.get('/items/tritanium')
        assert resp.status_code == 200

    def test_with_seeded_constant(self, db, client):
        from evebs.models import Constant
        region = make_region(db)
        make_trade_hub(db, region, system_id=30000142)
        make_item(db, cpp_eve_item_id=34, slug='tritanium')
        c = Constant(libe='taxes', f_value=1.10, description='Tax rate')
        db.session.add(c)
        db.session.commit()

        resp = client.get('/items/tritanium')
        assert resp.status_code == 200
