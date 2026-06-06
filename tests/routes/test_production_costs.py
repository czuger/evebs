"""Tests for evebs/routes/production_costs.py."""
import pytest

from tests.factories import make_item, make_blueprint, make_jma


class TestProductionCostsShow:
    def test_404_for_unknown_slug(self, client, db):
        resp = client.get('/production_costs/does-not-exist')
        assert resp.status_code == 404

    def test_400_for_base_item(self, client, db):
        item = make_item(db, slug='trit-base', base_item=True)
        db.session.commit()
        resp = client.get('/production_costs/trit-base')
        assert resp.status_code == 400

    def test_200_for_crafted_item_without_blueprint(self, client, db):
        item = make_item(db, item_id=99, slug='ammo', name='Fusion Charge S', base_item=False)
        db.session.commit()
        resp = client.get('/production_costs/ammo')
        assert resp.status_code == 200
        assert b'Fusion Charge S' in resp.data

    def test_200_for_crafted_item_with_blueprint(self, client, db):
        crafted = make_item(db, item_id=35, slug='ammo2')
        make_blueprint(db, crafted, manufacturing_cost=50.0)
        db.session.commit()
        resp = client.get('/production_costs/ammo2')
        assert resp.status_code == 200


class TestProductionCostsMaterials:
    def test_renders_materials_from_blueprint_tree(self, client, db):
        mat = make_item(db, item_id=34, slug='trit-pc', name='Tritanium')
        crafted = make_item(db, item_id=35, slug='ammo-pc', name='Ammo PC')
        bp = make_blueprint(db, crafted, prod_qtt=10)
        bp.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Tritanium', 'chain': {}}}
        make_jma(db, mat, min_sell_price=50.0)
        db.session.commit()

        resp = client.get('/production_costs/ammo-pc')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data

    def test_reaction_blueprint_with_authenticated_user_taxes(self, db, auth_client):
        mat = make_item(db, item_id=36, slug='full-pc', name='Fullerite')
        crafted = make_item(db, item_id=37, slug='c60-pc', name='Blue Pill PC')
        bp = make_blueprint(db, crafted, prod_qtt=1)
        bp.activity_type = 'reaction'
        bp.manufacturing_tree = {'36': {'quantity': 10, 'name': 'Fullerite', 'chain': {}}}
        make_jma(db, mat, min_sell_price=100.0)
        db.session.commit()

        client, user = auth_client
        user.industry_taxes = {
            'reaction': {'system_cost_index': 5.0, 'scc_tax': 4.0, 'reaction_tax': 2.0}
        }
        db.session.commit()

        resp = client.get('/production_costs/c60-pc')
        assert resp.status_code == 200

    def test_manufacturing_blueprint_with_authenticated_user_taxes(self, db, auth_client):
        mat = make_item(db, item_id=38, slug='nocx-pc', name='Noxcium')
        crafted = make_item(db, item_id=39, slug='bc-pc', name='Battlecruiser PC')
        bp = make_blueprint(db, crafted, prod_qtt=1)
        bp.manufacturing_tree = {'38': {'quantity': 20, 'name': 'Noxcium', 'chain': {}}}
        make_jma(db, mat, min_sell_price=200.0)
        db.session.commit()

        client, user = auth_client
        user.industry_taxes = {
            'manufacturing': {'system_cost_index': 3.0, 'scc_tax': 4.0, 'standard_tax': 1.0}
        }
        db.session.commit()

        resp = client.get('/production_costs/bc-pc')
        assert resp.status_code == 200
