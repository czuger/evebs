"""Unit tests for evebs/utils.py."""
from evebs.utils import SimplePagination


class TestSimplePagination:
    def test_basic_properties(self):
        p = SimplePagination(page=2, per_page=10, total=25)
        assert p.pages == 3
        assert p.has_prev is True
        assert p.has_next is True
        assert p.prev_num == 1
        assert p.next_num == 3

    def test_single_page(self):
        p = SimplePagination(page=1, per_page=10, total=5)
        assert p.pages == 1
        assert p.has_prev is False
        assert p.has_next is False

    def test_zero_total_gives_one_page(self):
        p = SimplePagination(page=1, per_page=10, total=0)
        assert p.pages == 1

    def test_iter_pages_few_pages_no_gaps(self):
        p = SimplePagination(page=1, per_page=10, total=30)
        pages = list(p.iter_pages())
        assert None not in pages
        assert pages == [1, 2, 3]

    def test_iter_pages_many_pages_has_ellipsis(self):
        p = SimplePagination(page=10, per_page=10, total=200)
        pages = list(p.iter_pages())
        assert None in pages
        assert 1 in pages
        assert 10 in pages
        assert 20 in pages

    def test_iter_pages_contiguous_small(self):
        p = SimplePagination(page=1, per_page=10, total=40)
        pages = list(p.iter_pages())
        assert None not in pages
        assert len(pages) == 4
