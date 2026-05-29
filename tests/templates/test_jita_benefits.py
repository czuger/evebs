from types import SimpleNamespace

from flask import render_template


def _render(app, **ctx):
    with app.test_request_context('/'):
        return render_template('jita_benefits/show.html', **ctx)


def _row(slug='tritanium', item_name='Tritanium', mg_name='Minerals',
         manufacturing_cost=1_000_000.0, manufacturing_tax=100_000.0,
         estimated_selling_price=1_500_000.0, selling_tax=75_000.0,
         benefit=325_000.0):
    mg = SimpleNamespace(name=mg_name) if mg_name else None
    eve_item = SimpleNamespace(slug=slug, id=1, name=item_name, market_group=mg)
    return SimpleNamespace(
        eve_item=eve_item,
        manufacturing_cost=manufacturing_cost,
        manufacturing_tax=manufacturing_tax,
        estimated_selling_price=estimated_selling_price,
        selling_tax=selling_tax,
        benefit=benefit,
    )


class TestJitaBenefitsTemplate:
    def test_renders_empty_state(self, app):
        html = _render(app, rows=[], pagination=None)
        assert 'No data' in html

    def test_renders_column_headers(self, app):
        html = _render(app, rows=[], pagination=None)
        assert 'Benefit' in html
        assert 'Manuf. cost' in html
        assert 'Est. sell price' in html

    def test_renders_item_name_and_link(self, app):
        html = _render(app, rows=[_row()], pagination=None)
        assert 'Tritanium' in html
        assert 'href="/items/tritanium"' in html

    def test_renders_market_group(self, app):
        html = _render(app, rows=[_row()], pagination=None)
        assert 'Minerals' in html

    def test_renders_row_without_market_group(self, app):
        html = _render(app, rows=[_row(mg_name=None)], pagination=None)
        assert 'Tritanium' in html
