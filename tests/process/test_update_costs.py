import pytest

from process.update_costs import update_base_item_costs, update_crafted_item_costs
from tests.factories import make_item, make_blueprint, make_constant


class TestUpdateBaseItemCosts:
    def test_sets_cost_from_weekly_avg_price(self, db):
        item = make_item(db, base_item=True, weekly_avg_price=100.0)
        update_base_item_costs()
        db.session.refresh(item)
        assert item.cost == pytest.approx(100.0)

    def test_skips_non_base_items(self, db):
        item = make_item(db, base_item=False, weekly_avg_price=200.0)
        update_base_item_costs()
        db.session.refresh(item)
        assert item.cost is None

    def test_noop_when_no_items(self, db):
        update_base_item_costs()  # must not raise

    def test_item_without_weekly_avg_price_gets_none_cost(self, db):
        item = make_item(db, base_item=True, weekly_avg_price=None)
        update_base_item_costs()
        db.session.refresh(item)
        assert item.cost is None


class TestUpdateCraftedItemCosts:
    def test_computes_cost_from_manufacturing_cost(self, db):
        crafted = make_item(db, item_id=35, slug='ammo', production_level=1)
        make_blueprint(db, crafted, nb_runs=1, prod_qtt=1, manufacturing_cost=50.0)
        make_constant(db, 'taxes', 1.1)
        update_crafted_item_costs(1)
        db.session.refresh(crafted)
        assert crafted.cost == pytest.approx(55.0)

    def test_cost_divided_by_prod_qtt(self, db):
        crafted = make_item(db, item_id=35, slug='ammo', production_level=1)
        make_blueprint(db, crafted, nb_runs=1, prod_qtt=10, manufacturing_cost=50.0)
        make_constant(db, 'taxes', 1.0)
        update_crafted_item_costs(1)
        db.session.refresh(crafted)
        assert crafted.cost == pytest.approx(5.0)

    def test_none_when_manufacturing_cost_missing(self, db):
        crafted = make_item(db, item_id=35, slug='ammo', production_level=1)
        make_blueprint(db, crafted, nb_runs=1, prod_qtt=1, manufacturing_cost=None)
        make_constant(db, 'taxes', 1.1)
        update_crafted_item_costs(1)
        db.session.refresh(crafted)
        assert crafted.cost is None

    def test_skips_when_taxes_constant_missing(self, db):
        crafted = make_item(db, item_id=35, slug='ammo', production_level=1)
        make_blueprint(db, crafted)
        update_crafted_item_costs(1)
        db.session.refresh(crafted)
        assert crafted.cost is None

    def test_only_updates_matching_production_level(self, db):
        item_l1 = make_item(db, item_id=35, slug='ammo1', production_level=1)
        item_l2 = make_item(db, item_id=36, slug='ammo2', production_level=2)
        make_blueprint(db, item_l1, blueprint_id=135, manufacturing_cost=10.0)
        make_blueprint(db, item_l2, blueprint_id=136, manufacturing_cost=10.0)
        make_constant(db, 'taxes', 1.0)
        update_crafted_item_costs(1)
        db.session.refresh(item_l1)
        db.session.refresh(item_l2)
        assert item_l1.cost == pytest.approx(10.0)
        assert item_l2.cost is None
