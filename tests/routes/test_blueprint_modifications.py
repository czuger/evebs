"""Tests for evebs/routes/blueprint_modifications.py."""
import pytest

from evebs.models import BlueprintModification
from tests.factories import make_item, make_blueprint


@pytest.fixture
def blueprint(db):
    item = make_item(db, item_id=34, slug='tritanium')
    bp = make_blueprint(db, item)
    bp.activity_type = 'manufacturing'
    db.session.commit()
    return bp


class TestEdit:
    def test_requires_auth(self, client, db, blueprint):
        resp = client.get(f'/blueprint_modifications/{blueprint.id}')
        assert resp.status_code in (301, 302)

    def test_200_for_valid_blueprint(self, auth_client, db, blueprint):
        client, _user = auth_client
        resp = client.get(f'/blueprint_modifications/{blueprint.id}')
        assert resp.status_code == 200
        assert b'Material reduction' in resp.data

    def test_404_for_unknown_blueprint(self, auth_client, db):
        client, _user = auth_client
        resp = client.get('/blueprint_modifications/99999')
        assert resp.status_code == 404

    def test_prefills_existing_reduction(self, auth_client, db, blueprint):
        client, user = auth_client
        db.session.add(BlueprintModification(
            user_id=user.id, blueprint_id=blueprint.id, percent_modification_value=0.9))
        db.session.commit()

        resp = client.get(f'/blueprint_modifications/{blueprint.id}')
        assert resp.status_code == 200
        assert b'10.0' in resp.data


class TestUpdate:
    def test_creates_row(self, auth_client, db, blueprint):
        client, user = auth_client
        resp = client.post(f'/blueprint_modifications/{blueprint.id}',
                           data={'reduction_pct': '10'})
        assert resp.status_code == 302

        mod = BlueprintModification.query.filter_by(
            user_id=user.id, blueprint_id=blueprint.id).one()
        assert mod.percent_modification_value == pytest.approx(0.9)
        assert mod.touched is True

    def test_updates_existing_row_without_duplicating(self, auth_client, db, blueprint):
        client, user = auth_client
        client.post(f'/blueprint_modifications/{blueprint.id}', data={'reduction_pct': '10'})
        client.post(f'/blueprint_modifications/{blueprint.id}', data={'reduction_pct': '25'})

        mods = BlueprintModification.query.filter_by(
            user_id=user.id, blueprint_id=blueprint.id).all()
        assert len(mods) == 1
        assert mods[0].percent_modification_value == pytest.approx(0.75)

    def test_clamps_out_of_range(self, auth_client, db, blueprint):
        client, user = auth_client
        client.post(f'/blueprint_modifications/{blueprint.id}', data={'reduction_pct': '150'})
        mod = BlueprintModification.query.filter_by(
            user_id=user.id, blueprint_id=blueprint.id).one()
        assert mod.percent_modification_value == pytest.approx(0.0)

    def test_non_numeric_defaults_to_no_reduction(self, auth_client, db, blueprint):
        client, user = auth_client
        client.post(f'/blueprint_modifications/{blueprint.id}', data={'reduction_pct': 'abc'})
        mod = BlueprintModification.query.filter_by(
            user_id=user.id, blueprint_id=blueprint.id).one()
        assert mod.percent_modification_value == pytest.approx(1.0)

    def test_404_for_unknown_blueprint(self, auth_client, db):
        client, _user = auth_client
        resp = client.post('/blueprint_modifications/99999', data={'reduction_pct': '10'})
        assert resp.status_code == 404
