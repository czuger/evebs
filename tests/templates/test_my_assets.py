from types import SimpleNamespace

from flask import render_template


def _render(app, **ctx):
    with app.test_request_context('/'):
        return render_template('my_assets/show.html', title='My assets', **ctx)


class TestMyAssetsTemplate:
    def test_renders_empty_state(self, app, user):
        html = _render(app, user=user, assets=[], stations=[])
        assert 'No assets.' in html

    def test_renders_asset_rows(self, app, user):
        asset = SimpleNamespace(quantity=5, universe_station_id=None)
        item = SimpleNamespace(name='Tritanium', slug='tritanium')
        html = _render(app, user=user, assets=[(asset, item, None)], stations=[])
        assert 'Tritanium' in html
        assert '5' in html

    def test_renders_station_selector_when_stations_present(self, app, db, user):
        from tests.factories import (
            make_universe_region, make_universe_constellation,
            make_universe_system, make_universe_station,
        )
        ur = make_universe_region(db, cpp_region_id=10000002)
        uc = make_universe_constellation(db, ur)
        us = make_universe_system(db, uc)
        st = make_universe_station(db, us)
        db.session.commit()
        html = _render(app, user=user, assets=[], stations=[st])
        assert 'Set station' in html
        assert st.name in html

    def test_station_option_selected_for_user_preference(self, app, db, user):
        from tests.factories import (
            make_universe_region, make_universe_constellation,
            make_universe_system, make_universe_station,
        )
        ur = make_universe_region(db, cpp_region_id=10000003)
        uc = make_universe_constellation(db, ur, cpp_constellation_id=20000021)
        us = make_universe_system(db, uc, cpp_system_id=30000143, name='Perimeter')
        st = make_universe_station(db, us, cpp_station_id=60003761)
        user.selected_assets_station_id = st.id
        db.session.commit()
        html = _render(app, user=user, assets=[], stations=[st])
        assert 'selected' in html
