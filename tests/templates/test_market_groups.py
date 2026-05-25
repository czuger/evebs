from flask import render_template

from tests.factories import make_market_group


def _render(app, **ctx):
    with app.test_request_context('/'):
        return render_template('market_groups/index.html', title='Market groups', **ctx)


class TestMarketGroupsTemplate:
    def test_renders_empty_list(self, app):
        html = _render(app, groups=[])
        assert 'Market groups' in html

    def test_renders_group_links(self, app, db):
        mg = make_market_group(db, cpp_market_group_id=1, name='Ammunition & Charges')
        db.session.commit()
        html = _render(app, groups=[mg])
        assert 'Ammunition &amp; Charges' in html
        assert f'/list_items?group_id={mg.id}' in html

    def test_renders_multiple_groups(self, app, db):
        mg1 = make_market_group(db, cpp_market_group_id=2, name='Ships')
        mg2 = make_market_group(db, cpp_market_group_id=3, name='Modules')
        db.session.commit()
        html = _render(app, groups=[mg1, mg2])
        assert 'Ships' in html
        assert 'Modules' in html
