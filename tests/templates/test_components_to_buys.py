from types import SimpleNamespace

from flask import render_template


def _render(app, **ctx):
    ctx.setdefault('stations', [])
    ctx.setdefault('known_structures', [])
    ctx.setdefault('unknown_structures', [])
    ctx.setdefault('selected_station_id', None)
    ctx.setdefault('asset_qty', {})
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

    def test_cost_and_volume_reflect_need_to_buy(self, app):
        """With stock deducted, cost/volume columns scale to the need-to-buy quantity."""
        c = SimpleNamespace(eve_item_id=34, eve_item_name='Tritanium',
                            qtt_to_buy=1000, total_cost=50000.0, required_volume=10.0)
        html = _render(app, components=[c], selected_station_id=99, asset_qty={34: 600})
        # need_to_buy = 400 → cost 50000*400/1000 = 20000 (20.0K), volume 10*400/1000 = 4.00
        assert '20.0K' in html      # need-to-buy cost
        assert '50.0K' not in html  # not the full-quantity cost
        assert '4.00' in html       # need-to-buy volume

    def test_fully_stocked_row_costs_zero(self, app):
        c = SimpleNamespace(eve_item_id=34, eve_item_name='Tritanium',
                            qtt_to_buy=1000, total_cost=50000.0, required_volume=10.0)
        html = _render(app, components=[c], selected_station_id=99, asset_qty={34: 1000})
        assert 'table-success' in html   # fully covered → green
        assert '50.0K' not in html       # nothing left to buy → cost not shown
