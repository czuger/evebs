from types import SimpleNamespace

from flask import render_template


def _render(app, **ctx):
    with app.test_request_context('/'):
        return render_template('user_sales_orders/show.html', title='My sales orders', **ctx)


class TestUserSalesOrdersTemplate:
    def test_renders_empty_state(self, app):
        html = _render(app, orders=[])
        assert 'No orders.' in html

    def test_renders_order_rows(self, app):
        order = SimpleNamespace(
            trade_hub_name='Jita',
            eve_item_id=34,
            eve_item_name='Tritanium',
            my_price=1000.0,
            min_price=900.0,
            price_delta=100.0,
            min_price_margin_pcent=0.11,
        )
        html = _render(app, orders=[order])
        assert 'Jita' in html
        assert 'Tritanium' in html

    def test_header_always_present(self, app):
        html = _render(app, orders=[])
        assert 'My sales orders' in html
        assert 'Trade hub' in html
