"""Tests for DownloadUniverseRegions.download — ESI HTTP mocked, real DB."""
import pytest
from unittest.mock import patch, MagicMock

from esi.download_universe_regions import DownloadUniverseRegions


def _mock_get(side_effect):
    mock = MagicMock()
    mock.ok = True
    mock.headers = {'x-pages': '1'}
    mock.json.side_effect = side_effect
    return mock


class TestDownloadUniverseRegions:
    def test_creates_new_regions(self, db):
        region_list = [10000002, 10000043]
        region_details = {
            10000002: {'name': 'The Forge', 'region_id': 10000002},
            10000043: {'name': 'Domain', 'region_id': 10000043},
        }

        def fake_get(url, **kwargs):
            r = MagicMock()
            r.ok = True
            r.headers = {'x-pages': '1'}
            if 'universe/regions/' in url and url.endswith('/'):
                # List endpoint
                try:
                    rid = int(url.rstrip('/').split('/')[-1])
                    r.json.return_value = region_details[rid]
                except (ValueError, KeyError):
                    r.json.return_value = region_list
            else:
                r.json.return_value = region_list
            return r

        with patch('esi.client.requests.get', side_effect=fake_get):
            DownloadUniverseRegions().download()

        from evebs.models import UniverseRegion
        names = {r.name for r in UniverseRegion.query.all()}
        assert 'The Forge' in names
        assert 'Domain' in names

    def test_updates_existing_region_name(self, db):
        from evebs.models import UniverseRegion
        existing = UniverseRegion(id=10000002, name='Old Name')
        db.session.add(existing)
        db.session.commit()

        def fake_get(url, **kwargs):
            r = MagicMock()
            r.ok = True
            r.headers = {'x-pages': '1'}
            if url.endswith('universe/regions/'):
                r.json.return_value = [10000002]
            else:
                r.json.return_value = {'name': 'The Forge', 'region_id': 10000002}
            return r

        with patch('esi.client.requests.get', side_effect=fake_get):
            DownloadUniverseRegions().download()

        db.session.expire(existing)
        assert existing.name == 'The Forge'

    def test_skips_region_with_empty_detail(self, db):
        def fake_get(url, **kwargs):
            r = MagicMock()
            r.ok = True
            r.headers = {'x-pages': '1'}
            if url.endswith('universe/regions/'):
                r.json.return_value = [10000002]
            else:
                r.json.return_value = None
            return r

        with patch('esi.client.requests.get', side_effect=fake_get):
            DownloadUniverseRegions().download()

        from evebs.models import UniverseRegion
        assert UniverseRegion.query.count() == 0
