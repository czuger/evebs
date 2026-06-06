"""Unit tests for model properties and classmethods."""
from datetime import datetime, timedelta


class TestUniverseStationProperties:
    def test_services_returns_empty_list_when_none(self, db):
        from evebs.models.tables.universe_station import UniverseStation
        s = UniverseStation()
        s._services = None
        assert s.services == []

    def test_services_setter_and_getter(self, db):
        from evebs.models.tables.universe_station import UniverseStation
        s = UniverseStation()
        s.services = ['manufacturing', 'research']
        assert s.services == ['manufacturing', 'research']

    def test_industry_costs_indices_returns_empty_dict_when_none(self, db):
        from evebs.models.tables.universe_station import UniverseStation
        s = UniverseStation()
        s._industry_costs_indices = None
        assert s.industry_costs_indices == {}

    def test_industry_costs_indices_setter_and_getter(self, db):
        from evebs.models.tables.universe_station import UniverseStation
        s = UniverseStation()
        s.industry_costs_indices = {'manufacturing': 0.05}
        assert s.industry_costs_indices == {'manufacturing': 0.05}


class TestUniverseRegionProperties:
    def test_market_items_returns_empty_list_when_none(self, db):
        from evebs.models.tables.universe_region import UniverseRegion
        r = UniverseRegion()
        r._market_items = None
        assert r.market_items == []

    def test_market_items_setter_and_getter(self, db):
        from evebs.models.tables.universe_region import UniverseRegion
        r = UniverseRegion()
        r.market_items = [34, 35, 36]
        assert r.market_items == [34, 35, 36]


class TestLastUpdateSet:
    def test_creates_new_record(self, db):
        from evebs.models import LastUpdate
        LastUpdate.set('test_create_unique')
        record = LastUpdate.query.filter_by(update_type='test_create_unique').first()
        assert record is not None

    def test_updates_existing_record(self, db):
        from evebs.models import LastUpdate
        old_dt = datetime.utcnow() - timedelta(hours=2)
        record = LastUpdate(update_type='test_update_unique', updated_at=old_dt)
        db.session.add(record)
        db.session.commit()

        LastUpdate.set('test_update_unique')
        db.session.expire(record)
        assert record.updated_at > old_dt


class TestEveItemsSavedListSetIds:
    def test_set_ids_serialises_to_json(self, db, user):
        from evebs.models import EveItemsSavedList
        sl = EveItemsSavedList(user_id=user.id, description='Test', saved_ids='[]')
        db.session.add(sl)
        db.session.flush()
        sl.set_ids([1, 2, 3])
        assert sl.saved_ids == '[1, 2, 3]'


class TestEveItemMarketGroupPath:
    def test_getter_parses_json(self, db):
        from evebs.models.tables.eve_item import EveItem
        item = EveItem()
        item._market_group_path = '[1, 2, 3]'
        assert item.market_group_path == [1, 2, 3]

    def test_setter_serialises_to_json(self, db):
        from evebs.models.tables.eve_item import EveItem
        item = EveItem()
        item.market_group_path = [4, 5, 6]
        assert item._market_group_path == '[4, 5, 6]'


class TestBlueprintBatchElementsCount:
    def test_batch_elements_count_is_prod_qtt_times_nb_runs(self, db):
        from evebs.models.tables.blueprint import Blueprint
        bp = Blueprint()
        bp.nb_runs = 5
        bp.prod_qtt = 10
        assert bp.batch_elements_count == 50
