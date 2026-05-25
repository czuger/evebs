from flask import render_template


class TestIndexTemplate:
    def test_renders_title(self, app):
        with app.test_request_context('/'):
            html = render_template('index.html', title='Eve Online Business Advisor')
        assert 'Eve Online Business Advisor' in html
