"""Unit tests for evebs/helpers.py."""
from datetime import datetime, timedelta

import pytest

from evebs.helpers import (
    _to_small_number, print_isk, print_pcent, print_volume,
    safe_multiply, show_last_update, meta_title,
)


class TestCurrentPage:
    def test_matches_current_path(self, app):
        from evebs.helpers import _current_page
        with app.test_request_context('/my-path'):
            assert _current_page('/my-path') is True
            assert _current_page('/other') is False


class TestToSmallNumber:
    def test_none_returns_na(self):
        assert _to_small_number(None) == 'N/A'

    def test_inf_returns_na(self):
        assert _to_small_number(float('inf')) == 'N/A'

    def test_billions_under_10(self):
        assert _to_small_number(1_500_000_000) == '1.50B'

    def test_billions_tens(self):
        assert _to_small_number(15_000_000_000) == '15.0B'

    def test_billions_hundreds(self):
        assert _to_small_number(150_000_000_000) == '150B'

    def test_millions_under_10(self):
        assert _to_small_number(1_500_000) == '1.50M'

    def test_millions_tens(self):
        assert _to_small_number(15_000_000) == '15.0M'

    def test_millions_hundreds(self):
        assert _to_small_number(150_000_000) == '150M'

    def test_thousands_under_10(self):
        assert _to_small_number(1_500) == '1.50K'

    def test_thousands_tens(self):
        assert _to_small_number(15_000) == '15.0K'

    def test_thousands_hundreds(self):
        assert _to_small_number(500_000) == '500K'

    def test_small_under_10(self):
        assert _to_small_number(5.5) == '5.50'

    def test_small_tens(self):
        assert _to_small_number(55.5) == '55.5'

    def test_small_hundreds(self):
        assert _to_small_number(555) == '555'

    def test_negative_millions(self):
        result = _to_small_number(-1_500_000)
        assert result == '-1.50M'


class TestPrintIsk:
    def test_none_returns_na(self):
        assert print_isk(None) == 'N/A'

    def test_inf_returns_na(self):
        assert print_isk(float('inf')) == 'N/A'

    def test_normal_value(self):
        assert print_isk(1_000_000) == '1.00M'


class TestPrintPcent:
    def test_none_returns_na(self):
        assert print_pcent(None) == 'N/A'

    def test_multiply_true(self):
        assert print_pcent(0.15, multiply=True) == '15.00 %'

    def test_multiply_false(self):
        assert print_pcent(15.0, multiply=False) == '15.00 %'


class TestPrintVolume:
    def test_none_returns_na(self):
        assert print_volume(None) == 'N/A'

    def test_normal_value(self):
        assert print_volume(1_000_000) == '1.00M'


class TestSafeMultiply:
    def test_none_first_arg(self):
        assert safe_multiply(None, 10) == float('inf')

    def test_none_second_arg(self):
        assert safe_multiply(10, None) == float('inf')

    def test_both_none(self):
        assert safe_multiply(None, None) == float('inf')

    def test_normal(self):
        assert safe_multiply(3, 4) == 12


class TestShowLastUpdate:
    def test_no_record_returns_empty(self, db):
        result = show_last_update('nonexistent_type')
        assert result == ''

    def test_today(self, db):
        from evebs.models import LastUpdate
        lu = LastUpdate(update_type='test_today', updated_at=datetime.utcnow())
        db.session.add(lu)
        db.session.commit()
        result = show_last_update('test_today')
        assert 'today' in result

    def test_yesterday(self, db):
        from evebs.models import LastUpdate
        lu = LastUpdate(update_type='test_yesterday',
                        updated_at=datetime.utcnow() - timedelta(days=1))
        db.session.add(lu)
        db.session.commit()
        result = show_last_update('test_yesterday')
        assert 'yesterday' in result

    def test_days_ago(self, db):
        from evebs.models import LastUpdate
        lu = LastUpdate(update_type='test_daysago',
                        updated_at=datetime.utcnow() - timedelta(days=5))
        db.session.add(lu)
        db.session.commit()
        result = show_last_update('test_daysago')
        assert 'days ago' in result


class TestMetaTitle:
    def test_with_title(self):
        result = meta_title('My Page')
        assert 'My Page' in result
        assert 'EVE Online' in result

    def test_without_title(self):
        result = meta_title()
        assert 'EveBusinessServer' in result
        assert 'EVE Online' in result
