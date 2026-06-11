"""Tests for download_market_histories — ESI HTTP mocked, real DB. Stores exact daily
history records from markets/{region}/history into market_histories."""
from datetime import date
from unittest.mock import patch, MagicMock

from esi.download_market_histories import download_market_histories, FORGE_REGION_ID
from evebs.models import MarketHistory
from tests.factories import make_universe_region


def _history():
    return [
        {'date': '2026-06-01', 'average': 10.0, 'highest': 12.0, 'lowest': 8.0,
         'order_count': 42, 'volume': 1000},
        {'date': '2026-06-02', 'average': 11.0, 'highest': 13.0, 'lowest': 9.0,
         'order_count': 50, 'volume': 1500},
    ]


def _fake_get(type_ids, history):
    def fake_get(url, **kwargs):
        r = MagicMock()
        r.ok = True
        r.headers = {'x-pages': '1'}
        if url.endswith('/types/'):
            r.json.return_value = type_ids
        elif '/history/' in url:
            r.json.return_value = history
        else:
            r.json.return_value = []
        return r
    return fake_get


class TestDownloadMarketHistories:
    def test_stores_exact_history_records(self, db):
        make_universe_region(db, region_id=10000043, name='Domain')
        db.session.commit()

        with patch('esi.client.requests.get', side_effect=_fake_get([35], _history())):
            summary = download_market_histories()

        rows = MarketHistory.query.order_by(MarketHistory.date).all()
        assert len(rows) == 2
        assert summary['records'] == 2

        first = rows[0]
        assert first.region_id == 10000043
        assert first.type_id == 35
        assert first.date == date(2026, 6, 1)
        assert first.average == 10.0
        assert first.highest == 12.0
        assert first.lowest == 8.0
        assert first.order_count == 42
        assert first.volume == 1000

    def test_forge_only_restricts_to_forge_region(self, db):
        make_universe_region(db, region_id=FORGE_REGION_ID, name='The Forge')
        make_universe_region(db, region_id=10000043, name='Domain')
        db.session.commit()

        with patch('esi.client.requests.get', side_effect=_fake_get([35], _history())):
            download_market_histories(forge_only=True)

        region_ids = {r.region_id for r in MarketHistory.query.all()}
        assert region_ids == {FORGE_REGION_ID}

    def test_idempotent_skips_existing_days(self, db):
        make_universe_region(db, region_id=10000043, name='Domain')
        db.session.commit()

        with patch('esi.client.requests.get', side_effect=_fake_get([35], _history())):
            download_market_histories()
            download_market_histories()   # second run — same (region, type, date) rows

        # on_conflict_do_nothing on (region_id, type_id, date) — no duplicates, no error.
        assert MarketHistory.query.count() == 2
