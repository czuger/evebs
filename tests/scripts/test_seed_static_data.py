"""Tests for scripts/seed_static_data.py seed functions."""
from unittest.mock import patch

from tests.factories import (
    make_universe_region, make_universe_constellation, make_universe_system,
    make_market_group,
)


def _patch_jsonl(data):
    return patch('scripts.seed_static_data._jsonl', return_value=iter(data))


class TestSeedRegions:
    def test_creates_new_regions(self, db):
        from scripts.seed_static_data import seed_regions
        from evebs.models import UniverseRegion

        with _patch_jsonl([{'_key': 10000002, 'name': {'en': 'The Forge'}}]):
            seed_regions(db, UniverseRegion)

        r = db.session.get(UniverseRegion, 10000002)
        assert r is not None
        assert r.name == 'The Forge'

    def test_updates_existing_region(self, db):
        from scripts.seed_static_data import seed_regions
        from evebs.models import UniverseRegion

        make_universe_region(db, region_id=10000002, name='Old Name')
        db.session.commit()

        with _patch_jsonl([{'_key': 10000002, 'name': {'en': 'The Forge'}}]):
            seed_regions(db, UniverseRegion)

        r = db.session.get(UniverseRegion, 10000002)
        assert r.name == 'The Forge'


class TestSeedMarketGroups:
    def test_creates_groups_with_parent_links(self, db):
        from scripts.seed_static_data import seed_market_groups
        from evebs.models import MarketGroup

        data = [
            {'_key': 1, 'name': {'en': 'Root'}, 'parentGroupID': None},
            {'_key': 2, 'name': {'en': 'Child'}, 'parentGroupID': 1},
        ]
        with _patch_jsonl(data):
            seed_market_groups(db, MarketGroup)

        root = db.session.get(MarketGroup, 1)
        child = db.session.get(MarketGroup, 2)
        assert root.parent_id is None
        assert child.parent_id == 1

    def test_skips_unresolved_parent(self, db):
        from scripts.seed_static_data import seed_market_groups
        from evebs.models import MarketGroup

        data = [{'_key': 5, 'name': {'en': 'Orphan'}, 'parentGroupID': 9999}]
        with _patch_jsonl(data):
            seed_market_groups(db, MarketGroup)

        orphan = db.session.get(MarketGroup, 5)
        assert orphan is not None
        assert orphan.parent_id is None


class TestSeedUniverse:
    def test_creates_constellations_and_systems(self, db):
        from scripts.seed_static_data import seed_universe
        from evebs.models import UniverseConstellation, UniverseSystem, UniverseRegion

        make_universe_region(db, region_id=10000002)
        db.session.commit()

        const_data = [{'_key': 20000020, 'name': {'en': 'Kimotoro'}, 'regionID': 10000002}]
        system_data = [{'_key': 30000142, 'name': {'en': 'Jita'}, 'constellationID': 20000020,
                        'securityStatus': 0.946, 'securityClass': 'B', 'starID': 40009083}]

        with patch('scripts.seed_static_data._jsonl', side_effect=[iter(const_data), iter(system_data)]):
            seed_universe(db, UniverseConstellation, UniverseSystem, UniverseRegion)

        uc = db.session.get(UniverseConstellation, 20000020)
        us = db.session.get(UniverseSystem, 30000142)
        assert uc is not None and uc.universe_region_id == 10000002
        assert us is not None and us.universe_constellation_id == 20000020
        assert us.star_id == 40009083

    def test_skips_system_with_unknown_constellation(self, db):
        from scripts.seed_static_data import seed_universe
        from evebs.models import UniverseConstellation, UniverseSystem, UniverseRegion

        make_universe_region(db, region_id=10000002)
        db.session.commit()

        const_data = []
        system_data = [{'_key': 30000142, 'name': {'en': 'Jita'}, 'constellationID': 99999}]

        with patch('scripts.seed_static_data._jsonl', side_effect=[iter(const_data), iter(system_data)]):
            seed_universe(db, UniverseConstellation, UniverseSystem, UniverseRegion)

        assert UniverseSystem.query.count() == 0


class TestSeedStations:
    def test_creates_stations(self, db):
        from scripts.seed_static_data import seed_stations
        from evebs.models import UniverseStation

        ur = make_universe_region(db)
        uc = make_universe_constellation(db, ur)
        us = make_universe_system(db, uc, system_id=30000142)
        db.session.commit()

        data = [{'_key': 60003760, 'solarSystemID': 30000142}]
        with _patch_jsonl(data):
            seed_stations(db, UniverseStation, __import__('evebs.models', fromlist=['UniverseSystem']).UniverseSystem)

        st = db.session.get(UniverseStation, 60003760)
        assert st is not None
        assert st.universe_system_id == 30000142

    def test_skips_station_with_unknown_system(self, db):
        from scripts.seed_static_data import seed_stations
        from evebs.models import UniverseStation, UniverseSystem

        data = [{'_key': 60003760, 'solarSystemID': 99999999}]
        with _patch_jsonl(data):
            seed_stations(db, UniverseStation, UniverseSystem)

        assert UniverseStation.query.count() == 0
