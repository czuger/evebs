from flask import render_template

from tests.factories import (
    make_item, make_blueprint, make_blueprint_material, make_universe_region,
)


def _render(app, template, **ctx):
    with app.test_request_context('/'):
        return render_template(template, **ctx)


class TestProductionCostsShowTemplate:
    def test_renders_item_without_blueprint(self, app, db):
        item = make_item(db, slug='ammo')
        db.session.commit()
        html = _render(app, 'production_costs/show.html', item=item, taxes=1.13, title='T')
        assert 'Total for batch' in html

    def test_renders_item_with_blueprint(self, app, db):
        mat = make_item(db, cpp_eve_item_id=34, slug='trit', cost=10.0)
        crafted = make_item(db, cpp_eve_item_id=35, slug='ammo')
        bp = make_blueprint(db, crafted, prod_qtt=1)
        make_blueprint_material(db, bp, mat, required_qtt=5)
        db.session.commit()
        html = _render(app, 'production_costs/show.html', item=crafted, taxes=1.1, title='T')
        assert mat.name in html
        assert 'Batch size' in html
        assert 'Final cost' in html

    def test_renders_taxes_percentage(self, app, db):
        item = make_item(db, slug='ammo2')
        make_blueprint(db, item)
        db.session.commit()
        html = _render(app, 'production_costs/show.html', item=item, taxes=1.13, title='T')
        assert '13.0' in html


class TestDailiesAvgPricesTemplate:
    def test_renders_empty_list(self, app, db):
        item = make_item(db, slug='trit2')
        db.session.commit()
        html = _render(app, 'production_costs/dailies_avg_prices.html',
                       item=item, dailies_details=[], pagination=None, title='T')
        assert item.name in html

    def test_renders_with_rows(self, app, db):
        from types import SimpleNamespace
        from datetime import date
        item = make_item(db, slug='trit3')
        db.session.commit()
        row = SimpleNamespace(day=date.today(), volume=500, weighted_avg_price=123.45)
        html = _render(app, 'production_costs/dailies_avg_prices.html',
                       item=item, dailies_details=[row], pagination=None, title='T')
        assert str(date.today()) in html


class TestMarketHistoriesTemplate:
    def test_renders_empty_list(self, app, db):
        item = make_item(db, slug='trit4')
        db.session.commit()
        html = _render(app, 'production_costs/market_histories.html',
                       item=item, market_histories=[], title='T')
        assert item.name in html

    def test_renders_with_rows(self, app, db):
        from types import SimpleNamespace
        item = make_item(db, slug='trit5')
        db.session.commit()
        region = SimpleNamespace(name='The Forge')
        row = SimpleNamespace(universe_region=region, volume=10000,
                              average=50.0, highest=60.0, lowest=40.0)
        html = _render(app, 'production_costs/market_histories.html',
                       item=item, market_histories=[row], title='T')
        assert 'The Forge' in html
