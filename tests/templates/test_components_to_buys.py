from types import SimpleNamespace

from flask import render_template


def _render(app, **ctx):
    with app.test_request_context('/'):
        return render_template('components_to_buys/show.html', title='Components to buy', **ctx)


class TestComponentsToBuyTemplate:
    def test_renders_empty_state(self, app):
        html = _render(app, components=[])
        assert 'Nothing to buy.' in html

    def test_renders_component_rows(self, app):
        c = SimpleNamespace(eve_item_id=34, eve_item_name='Tritanium',
                            qtt_to_buy=1000, total_cost=50000.0, required_volume=5.0)
        html = _render(app, components=[c])
        assert 'Tritanium' in html

    def test_header_always_present(self, app):
        html = _render(app, components=[])
        assert 'Components to buy' in html
        assert 'Qty to buy' in html
