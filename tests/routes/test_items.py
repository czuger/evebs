"""Tests for evebs/routes/items.py."""
import pytest
from tests.factories import make_universe_system, make_trade_hub, make_item, make_market_group


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

