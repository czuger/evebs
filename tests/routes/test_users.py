"""Tests for evebs/routes/users.py."""
import pytest
from tests.factories import (
    make_universe_region, make_universe_constellation,
    make_universe_system, make_universe_station,
)


class TestUsersEdit:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/users/edit')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        resp = client.get('/users/edit')
        assert resp.status_code == 200


class TestUsersUpdate:
    def test_redirects_unauthenticated(self, client):
        resp = client.post('/users', data={'min_margin_percent': 15})
        assert resp.status_code == 302

    def test_updates_numeric_settings(self, db, auth_client):
        client, user = auth_client
        resp = client.post('/users', data={
            'min_margin_percent':         '25',
            'min_batch_margin_amount':    '10000000',
            'buy_min_margin_percent':     '15',
            'buy_min_batch_margin_amount': '3000000',
        })
        assert resp.status_code == 302

        db.session.expire(user)
        assert user.sell_orders_filtering['min_margin_percent'] == 25
        assert user.sell_orders_filtering['min_batch_margin_amount'] == 10_000_000
        assert user.buy_order_filtering['min_margin_percent'] == 15
        assert user.buy_order_filtering['min_batch_margin_amount'] == 3_000_000

    def test_enables_show_selected_items(self, db, auth_client):
        client, user = auth_client
        client.post('/users', data={'sell_show_selected_items': 'on', 'buy_show_selected_items': 'on'})
        db.session.expire(user)
        assert user.sell_orders_filtering['show_selected_items'] is True
        assert user.buy_order_filtering['show_selected_items'] is True

    def test_disables_show_selected_items(self, db, auth_client):
        client, user = auth_client
        client.post('/users', data={})  # both absent → False
        db.session.expire(user)
        assert user.sell_orders_filtering['show_selected_items'] is False
        assert user.buy_order_filtering['show_selected_items'] is False

    def test_enables_hide_low_confidence(self, db, auth_client):
        client, user = auth_client
        client.post('/users', data={'sell_hide_low_confidence': 'on'})
        db.session.expire(user)
        assert user.sell_orders_filtering['hide_low_confidence'] is True

    def test_disables_hide_low_confidence(self, db, auth_client):
        client, user = auth_client
        client.post('/users', data={})  # absent → False
        db.session.expire(user)
        assert user.sell_orders_filtering['hide_low_confidence'] is False

    def test_invalid_input_redirects_without_error(self, db, auth_client):
        client, user = auth_client
        original = (user.sell_orders_filtering or {}).get('min_margin_percent', 20)
        resp = client.post('/users', data={'min_margin_percent': 'not_a_number'})
        assert resp.status_code == 302
        db.session.expire(user)
        assert user.sell_orders_filtering['min_margin_percent'] == original

    def test_amount_with_spaces_accepted(self, db, auth_client):
        client, user = auth_client
        client.post('/users', data={'min_batch_margin_amount': '10 000 000'})
        db.session.expire(user)
        assert user.sell_orders_filtering['min_batch_margin_amount'] == 10_000_000


class TestUsersEditWithStation:
    def test_returns_200_with_current_station(self, db, auth_client):
        ur = make_universe_region(db, region_id=10000099)
        uc = make_universe_constellation(db, ur, constellation_id=20000099)
        us = make_universe_system(db, uc, system_id=30000999, name='TestSys')
        st = make_universe_station(db, us, station_id=60009999)
        db.session.commit()

        client, user = auth_client
        user.current_location_station_id = st.id
        db.session.commit()

        resp = client.get('/users/edit')
        assert resp.status_code == 200


class TestUsersSalesTaxes:
    def test_get_returns_200(self, auth_client):
        client, _ = auth_client
        resp = client.get('/users/sales_taxes')
        assert resp.status_code == 200

    def test_post_updates_and_redirects(self, db, auth_client):
        client, user = auth_client
        resp = client.post('/users/sales_taxes', data={
            'broker_fee_taxes': '2.0',
            'sales_taxes': '3.5',
            'safety_tax': '0.5',
        })
        assert resp.status_code == 302
        db.session.expire(user)
        assert user.sales_taxes['broker_fee_taxes'] == 2.0
        assert user.sales_taxes['sales_taxes'] == 3.5


class TestUsersIndustryTaxes:
    def test_get_returns_200(self, auth_client):
        client, _ = auth_client
        resp = client.get('/users/industry_taxes')
        assert resp.status_code == 200

    def test_post_updates_and_redirects(self, db, auth_client):
        client, user = auth_client
        resp = client.post('/users/industry_taxes', data={
            'mfg_sci': '5.0',
            'mfg_scc': '4.0',
            'mfg_std': '1.0',
        })
        assert resp.status_code == 302
        db.session.expire(user)
        assert user.industry_taxes['manufacturing']['system_cost_index'] == 5.0

    def test_invalid_tax_value_defaults_to_zero(self, db, auth_client):
        client, user = auth_client
        client.post('/users/industry_taxes', data={'mfg_sci': 'bad_value'})
        db.session.expire(user)
        assert user.industry_taxes['manufacturing']['system_cost_index'] == 0.0

    def test_industry_taxes_no_longer_holds_reaction(self, db, auth_client):
        client, user = auth_client
        client.post('/users/industry_taxes', data={'mfg_sci': '5.0'})
        db.session.expire(user)
        assert 'reaction' not in user.industry_taxes


class TestUsersReactionModifications:
    def test_get_returns_200(self, auth_client):
        client, _ = auth_client
        assert client.get('/users/reaction_modifications').status_code == 200

    def test_post_updates_and_redirects(self, db, auth_client):
        client, user = auth_client
        resp = client.post('/users/reaction_modifications', data={
            'rxn_sci': '5.0', 'rxn_scc': '4.0', 'rxn_tax': '2.0',
            'rxn_material_consumption': '-2.5',
        })
        assert resp.status_code == 302
        db.session.expire(user)
        assert user.reaction_modifications['reaction_tax'] == 2.0
        assert user.reaction_modifications['material_consumption'] == -2.5

    def test_positive_material_consumption_clamped_to_zero(self, db, auth_client):
        client, user = auth_client
        client.post('/users/reaction_modifications', data={
            'rxn_sci': '5', 'rxn_scc': '4', 'rxn_tax': '1', 'rxn_material_consumption': '3',
        })
        db.session.expire(user)
        assert user.reaction_modifications['material_consumption'] == 0.0
