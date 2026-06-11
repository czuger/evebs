"""Tests for evebs/routes/user_industry_costs.py."""
import pytest

from tests.factories import (
    make_universe_region, make_universe_constellation, make_universe_system,
    make_item, make_blueprint, make_jita_min_price, remove_jita_min_price,
)


@pytest.fixture
def seeded(db):
    """Two blueprints (manufacturing + reaction) with fully-priced materials."""
    mat = make_item(db, item_id=34, slug='tritanium', name='Tritanium')
    prod_mfg = make_item(db, item_id=35, slug='ammo', name='Ammo')
    prod_rxn = make_item(db, item_id=36, slug='fuel', name='Fuel Block')

    bp_mfg = make_blueprint(db, prod_mfg, blueprint_id=10035, nb_runs=1, prod_qtt=10)
    bp_mfg.activity_type = 'manufacturing'
    bp_mfg.manufacturing_tree = {'34': {'quantity': 100, 'name': 'Tritanium', 'chain': {}}}

    bp_rxn = make_blueprint(db, prod_rxn, blueprint_id=10036, nb_runs=1, prod_qtt=40)
    bp_rxn.activity_type = 'reaction'
    bp_rxn.manufacturing_tree = {'34': {'quantity': 400, 'name': 'Tritanium', 'chain': {}}}

    make_jita_min_price(db, mat, min_sell_price=5.0)
    make_jita_min_price(db, prod_mfg, min_sell_price=200.0)
    make_jita_min_price(db, prod_rxn, min_sell_price=80.0)

    db.session.commit()
    return {'mat': mat, 'prod_mfg': prod_mfg, 'prod_rxn': prod_rxn}


class TestUserIndustryCosts:
    def test_manufacturing_redirects_unauthenticated(self, client):
        resp = client.get('/user_industry_costs/manufacturing')
        assert resp.status_code == 302

    def test_reaction_redirects_unauthenticated(self, client):
        resp = client.get('/user_industry_costs/reaction')
        assert resp.status_code == 302

    def test_manufacturing_returns_200(self, auth_client):
        client, _ = auth_client
        resp = client.get('/user_industry_costs/manufacturing')
        assert resp.status_code == 200

    def test_reaction_returns_200(self, auth_client):
        client, _ = auth_client
        resp = client.get('/user_industry_costs/reaction')
        assert resp.status_code == 200

    def test_manufacturing_shows_item(self, db, auth_client, seeded):
        client, _ = auth_client
        resp = client.get('/user_industry_costs/manufacturing')
        assert resp.status_code == 200
        assert b'Ammo' in resp.data

    def test_manufacturing_does_not_show_reaction_item(self, db, auth_client, seeded):
        client, _ = auth_client
        resp = client.get('/user_industry_costs/manufacturing')
        assert b'Fuel Block' not in resp.data

    def test_reaction_shows_item(self, db, auth_client, seeded):
        client, _ = auth_client
        resp = client.get('/user_industry_costs/reaction')
        assert resp.status_code == 200
        assert b'Fuel Block' in resp.data

    def test_reaction_does_not_show_manufacturing_item(self, db, auth_client, seeded):
        client, _ = auth_client
        resp = client.get('/user_industry_costs/reaction')
        assert b'Ammo' not in resp.data

    def test_item_missing_jma_price_excluded(self, db, auth_client, seeded):
        """Blueprint whose material has no JMA price must not appear."""
        remove_jita_min_price(db, seeded['mat'])
        db.session.commit()
        client, _ = auth_client
        resp = client.get('/user_industry_costs/manufacturing')
        assert resp.status_code == 200
        assert b'Ammo' not in resp.data

    def test_no_null_error_with_default_taxes(self, db, auth_client, seeded):
        """The margin comparison must not raise TypeError when taxes are at default values."""
        client, _ = auth_client
        resp = client.get('/user_industry_costs/manufacturing')
        # Would 500 if margin_per_unit comparison with None blew up
        assert resp.status_code == 200

    def test_shows_user_name(self, db, auth_client, seeded):
        client, user = auth_client
        resp = client.get('/user_industry_costs/manufacturing')
        assert user.name.encode() in resp.data

    def test_shows_active_tax_rates(self, db, auth_client, seeded):
        client, _ = auth_client
        resp = client.get('/user_industry_costs/manufacturing')
        # The tax summary header should mention percent signs
        assert b'%' in resp.data

    def test_links_to_industry_taxes_settings(self, db, auth_client, seeded):
        client, _ = auth_client
        resp = client.get('/user_industry_costs/manufacturing')
        assert b'industry_taxes' in resp.data

    def test_pagination_param_accepted(self, auth_client):
        client, _ = auth_client
        resp = client.get('/user_industry_costs/manufacturing?page=1')
        assert resp.status_code == 200
