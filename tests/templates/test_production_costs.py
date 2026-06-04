from types import SimpleNamespace
from flask import render_template

from tests.factories import make_item, make_blueprint


def _render(app, template, **ctx):
    with app.test_request_context('/'):
        return render_template(template, **ctx)


class TestProductionCostsShowTemplate:
    def test_renders_item_without_blueprint(self, app, db):
        item = make_item(db, slug='ammo')
        db.session.commit()
        html = _render(app, 'production_costs/show.html', item=item, materials=[], taxes=1.13, title='T')
        assert 'Total for batch' in html

    def test_renders_item_with_materials(self, app, db):
        mat = make_item(db, item_id=34, slug='trit')
        crafted = make_item(db, item_id=35, slug='ammo')
        make_blueprint(db, crafted, prod_qtt=1, manufacturing_cost=50.0)
        db.session.commit()
        materials = [SimpleNamespace(required_qtt=5, eve_item=mat, jita_price=10.0)]
        html = _render(app, 'production_costs/show.html', item=crafted, materials=materials, taxes=1.1, title='T')
        assert mat.name in html
        assert 'Batch size' in html
        assert 'Final cost' in html

    def test_renders_taxes_percentage(self, app, db):
        item = make_item(db, slug='ammo2')
        make_blueprint(db, item)
        db.session.commit()
        html = _render(app, 'production_costs/show.html', item=item, materials=[], taxes=1.13, title='T')
        assert '13.0' in html


class TestDailiesAvgPricesTemplate:
    def test_renders_empty_list(self, app, db):
        item = make_item(db, slug='trit2')
        db.session.commit()
        html = _render(app, 'production_costs/dailies_avg_prices.html',
                       item=item, dailies_details=[], pagination=None, title='T')
        assert item.name in html

    def test_renders_with_rows(self, app, db):
        from datetime import date
        item = make_item(db, slug='trit3')
        db.session.commit()
        row = SimpleNamespace(day=date.today(), volume=500, weighted_avg_price=123.45)
        html = _render(app, 'production_costs/dailies_avg_prices.html',
                       item=item, dailies_details=[row], pagination=None, title='T')
        assert str(date.today()) in html
