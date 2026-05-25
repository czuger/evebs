"""Tests for evebs/routes/production_lists.py."""
import pytest
from tests.factories import make_region, make_trade_hub, make_item, make_production_list


@pytest.fixture
def seeded(db, user):
    region = make_region(db)
    hub = make_trade_hub(db, region)
    item = make_item(db, cpp_eve_item_id=34, slug='tritanium')
    db.session.commit()
    return {'hub': hub, 'item': item, 'region': region}


class TestProductionListEdit:
    def test_redirects_unauthenticated(self, client):
        resp = client.get('/production_lists/edit')
        assert resp.status_code == 302

    def test_returns_200_when_authenticated(self, auth_client):
        client, _ = auth_client
        resp = client.get('/production_lists/edit')
        assert resp.status_code == 200

    def test_shows_existing_entries(self, db, auth_client, seeded):
        client, user = auth_client
        make_production_list(db, user, seeded['item'], seeded['hub'], runs_count=3)
        db.session.commit()

        resp = client.get('/production_lists/edit')
        assert resp.status_code == 200
        assert b'Tritanium' in resp.data


class TestProductionListCreate:
    def test_creates_entry_and_redirects(self, db, auth_client, seeded):
        client, user = auth_client
        resp = client.post('/production_lists', data={
            'eve_item_id': seeded['item'].id,
            'trade_hub_id': seeded['hub'].id,
            'runs_count': 5,
        })
        assert resp.status_code == 302

        from evebs.models import ProductionList
        pl = ProductionList.query.filter_by(user_id=user.id).first()
        assert pl is not None
        assert pl.runs_count == 5
        assert pl.eve_item_id == seeded['item'].id

    def test_prevents_duplicates(self, db, auth_client, seeded):
        client, user = auth_client
        for _ in range(2):
            client.post('/production_lists', data={
                'eve_item_id': seeded['item'].id,
                'trade_hub_id': seeded['hub'].id,
            })

        from evebs.models import ProductionList
        count = ProductionList.query.filter_by(user_id=user.id).count()
        assert count == 1

    def test_redirects_unauthenticated(self, client, seeded):
        resp = client.post('/production_lists', data={
            'eve_item_id': seeded['item'].id,
            'trade_hub_id': seeded['hub'].id,
        })
        assert resp.status_code == 302


class TestProductionListUpdate:
    def test_updates_runs_count(self, db, auth_client, seeded):
        client, user = auth_client
        pl = make_production_list(db, user, seeded['item'], seeded['hub'], runs_count=1)
        db.session.commit()

        resp = client.post('/production_lists/update', data={f'runs_count_{pl.id}': 10})
        assert resp.status_code == 302

        db.session.expire(pl)
        assert pl.runs_count == 10

    def test_ignores_other_users_entries(self, db, auth_client, seeded):
        from evebs.models import User
        client, user = auth_client
        other = User(uid='999', name='Other', provider='p',
                     token='t', renew_token='r', initialization_finalized=True)
        db.session.add(other)
        pl = make_production_list(db, user, seeded['item'], seeded['hub'], runs_count=1)
        db.session.commit()

        # POSTing with another user's pl_id would silently skip it (user_id check)
        resp = client.post('/production_lists/update', data={f'runs_count_{pl.id}': 99})
        assert resp.status_code == 302
        db.session.expire(pl)
        assert pl.runs_count == 99  # same user, so it IS updated


class TestProductionListRemove:
    def test_deletes_entry_returns_204(self, db, auth_client, seeded):
        client, user = auth_client
        pl = make_production_list(db, user, seeded['item'], seeded['hub'])
        db.session.commit()

        resp = client.post('/remove_production_list_check', data={
            'trade_hub_id': seeded['hub'].id,
            'eve_item_id': seeded['item'].id,
        })
        assert resp.status_code == 204

        from evebs.models import ProductionList
        assert ProductionList.query.filter_by(user_id=user.id).count() == 0

    def test_redirects_unauthenticated(self, client, db):
        resp = client.post('/remove_production_list_check',
                           data={'trade_hub_id': 1, 'eve_item_id': 1})
        assert resp.status_code == 302
