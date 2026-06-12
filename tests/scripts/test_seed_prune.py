"""Tests for the eve_items prune in scripts/seed_static_data.py (_prune_to_keep)."""
from evebs.models import (
    EveItem, MarketGroup, ProductionList, PublicTradeOrder, SalesFinal, UserSaleOrder, UserAsset,
)
from evebs.models.tables.associations import eve_items_users
from scripts.seed_static_data import _prune_to_keep, _prune_empty_market_groups
from tests.factories import (
    make_item, make_market_group, make_universe_system, make_production_list,
    make_public_trade_order, make_sales_final, make_user_sale_order, make_user_asset,
)


class TestPruneToKeep:
    def test_removes_unkept_items_and_their_children(self, db, user):
        keep_id, drop_id = 34, 99999
        system = make_universe_system(db)            # Jita, id 30000142
        keep = make_item(db, item_id=keep_id, name='Tritanium', slug='tritanium')
        drop = make_item(db, item_id=drop_id, name='Junk', slug='junk')

        # Children attached to the item that will be pruned (must all be removed).
        make_production_list(db, user, drop, system)
        make_public_trade_order(db, drop, system, order_id=5001)
        make_sales_final(db, drop, system, order_id=5002)
        make_user_sale_order(db, user, drop, system)
        make_user_asset(db, user, drop)
        db.session.execute(eve_items_users.insert().values(user_id=user.id, eve_item_id=drop.id))
        # A child on the kept item (must survive).
        make_production_list(db, user, keep, system)
        db.session.commit()

        removed = _prune_to_keep(db, {keep_id})

        assert removed['eve_items'] == 1
        # Fresh queries with literal ids — the raw bulk delete bypasses the ORM identity
        # map, so the `keep`/`drop` instances are stale and must not be touched.
        assert EveItem.query.filter_by(id=drop_id).count() == 0
        assert EveItem.query.filter_by(id=keep_id).count() == 1

        # Every child of the dropped item is gone (RESTRICT + ORM-cascade tables alike).
        assert ProductionList.query.filter_by(eve_item_id=drop_id).count() == 0
        assert PublicTradeOrder.query.filter_by(eve_item_id=drop_id).count() == 0
        assert SalesFinal.query.filter_by(eve_item_id=drop_id).count() == 0
        assert UserSaleOrder.query.filter_by(eve_item_id=drop_id).count() == 0
        assert UserAsset.query.filter_by(eve_item_id=drop_id).count() == 0
        assert db.session.execute(
            eve_items_users.select().where(eve_items_users.c.eve_item_id == drop_id)
        ).first() is None

        # The kept item and its child survive.
        assert ProductionList.query.filter_by(eve_item_id=keep_id).count() == 1


class TestPruneEmptyMarketGroups:
    def test_removes_groups_with_no_items_keeps_ancestors(self, db):
        root = make_market_group(db, group_id=1, name='Root')
        mid = make_market_group(db, group_id=2, name='Mid', parent=root)
        leaf = make_market_group(db, group_id=3, name='Leaf', parent=mid)
        make_market_group(db, group_id=4, name='EmptyChild', parent=root)   # no items
        make_market_group(db, group_id=5, name='OrphanEmpty')               # no items, no parent
        make_item(db, item_id=34, slug='trit', market_group=leaf)
        db.session.commit()

        removed = _prune_empty_market_groups(db)

        assert removed == 2
        # Group with the item plus its ancestor chain survive; the empty ones are gone.
        assert {g.id for g in MarketGroup.query.all()} == {1, 2, 3}
