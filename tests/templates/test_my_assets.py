from types import SimpleNamespace

from flask import render_template


def _render(app, **ctx):
    ctx.setdefault('stations', [])
    ctx.setdefault('known_structures', [])
    ctx.setdefault('unknown_structures', [])
    ctx.setdefault('selected_location_id', None)
    with app.test_request_context('/'):
        return render_template('my_assets/show.html', title='My assets', **ctx)


def _asset(quantity=5, station_id=None, structure_id=None):
    return SimpleNamespace(quantity=quantity,
                           universe_station_id=station_id,
                           universe_structure_id=structure_id)


class TestMyAssetsTemplate:
    def test_renders_empty_state(self, app, user):
        html = _render(app, user=user, assets=[])
        assert 'No assets.' in html

    def test_renders_asset_at_station(self, app, user):
        asset = _asset(quantity=5)
        item = SimpleNamespace(name='Tritanium', slug='tritanium')
        station = SimpleNamespace(name='Jita IV', id=60003760)
        html = _render(app, user=user, assets=[(asset, item, station, None, None)])
        assert 'Tritanium' in html
        assert '5' in html
        assert 'Jita IV' in html

    def test_renders_asset_at_known_structure(self, app, user):
        asset = _asset(quantity=3, structure_id=1_000_000_000_001)
        item = SimpleNamespace(name='Rifter', slug='rifter')
        structure = SimpleNamespace(name='Jita Trade Hub Alpha', id=1_000_000_000_001)
        html = _render(app, user=user, assets=[(asset, item, None, structure, None)])
        assert 'Jita Trade Hub Alpha' in html

    def test_renders_asset_at_unknown_structure(self, app, user):
        asset = _asset(quantity=2, structure_id=1_000_000_000_002)
        item = SimpleNamespace(name='Rifter', slug='rifter')
        unknown = SimpleNamespace(name='XY-123', id=1_000_000_000_002)
        html = _render(app, user=user, assets=[(asset, item, None, None, unknown)])
        assert 'XY-123' in html
        assert 'Unknown structure' not in html

    def test_renders_dash_when_no_location(self, app, user):
        asset = _asset(quantity=1)
        item = SimpleNamespace(name='Tritanium', slug='tritanium')
        html = _render(app, user=user, assets=[(asset, item, None, None, None)])
        assert '—' in html

    def test_renders_station_selector_when_stations_present(self, app, db, user):
        from tests.factories import (
            make_universe_region, make_universe_constellation,
            make_universe_system, make_universe_station,
        )
        ur = make_universe_region(db, region_id=10000002)
        uc = make_universe_constellation(db, ur)
        us = make_universe_system(db, uc)
        st = make_universe_station(db, us)
        db.session.commit()
        html = _render(app, user=user, assets=[], stations=[st])
        assert 'Filter' in html
        assert st.name in html

    def test_station_option_selected_for_user_preference(self, app, db, user):
        from tests.factories import (
            make_universe_region, make_universe_constellation,
            make_universe_system, make_universe_station,
        )
        ur = make_universe_region(db, region_id=10000003)
        uc = make_universe_constellation(db, ur, constellation_id=20000021)
        us = make_universe_system(db, uc, system_id=30000143, name='Perimeter')
        st = make_universe_station(db, us, station_id=60003761)
        db.session.commit()
        html = _render(app, user=user, assets=[], stations=[st],
                       selected_location_id=st.id)
        assert 'selected' in html

    def test_unknown_structure_shown_in_dropdown(self, app, user):
        unknown = SimpleNamespace(name='ZZ-999', id=1_000_000_000_003)
        html = _render(app, user=user, assets=[], unknown_structures=[unknown])
        assert 'ZZ-999' in html
        assert 'Filter' in html
