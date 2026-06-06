from types import SimpleNamespace

from flask import render_template

from tests.factories import make_item, make_blueprint


def _render(app, **ctx):
    defaults = {
        'prod_qtt': 1,
        'batch_mat_cost': 0.0,
        'unit_mat_cost': 0.0,
        'sci': 5.0,
        'unit_sci_cost': 0.0,
        'scc': 4.0,
        'unit_scc_cost': 0.0,
        'act_tax': 1.0,
        'act_tax_label': 'Standard tax',
        'unit_act_cost': 0.0,
        'unit_tax_total': 0.0,
        'unit_total': 0.0,
        'jita_system_id': 30000142,
    }
    defaults.update(ctx)
    with app.test_request_context('/'):
        return render_template('production_costs/show.html', **defaults)


class TestProductionCostsShowTemplate:
    def test_renders_item_without_blueprint(self, app, db):
        item = make_item(db, slug='ammo')
        db.session.commit()
        html = _render(app, item=item, materials=[], title='T')
        assert 'Total cost' in html

    def test_renders_item_with_materials(self, app, db):
        mat = make_item(db, item_id=34, slug='trit')
        crafted = make_item(db, item_id=35, slug='ammo')
        make_blueprint(db, crafted, prod_qtt=1, manufacturing_cost=50.0)
        db.session.commit()
        materials = [SimpleNamespace(required_qtt=5, eve_item=mat, jita_price=10.0)]
        html = _render(app, item=crafted, materials=materials,
                       batch_mat_cost=50.0, unit_mat_cost=50.0, title='T')
        assert mat.name in html
        assert 'Per unit' in html
        assert 'Total cost' in html

    def test_renders_taxes_percentage(self, app, db):
        item = make_item(db, slug='ammo2')
        make_blueprint(db, item)
        db.session.commit()
        html = _render(app, item=item, materials=[], sci=13.0, title='T')
        assert '13.0' in html
