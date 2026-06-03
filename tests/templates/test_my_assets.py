from types import SimpleNamespace

from flask import render_template


def _render(app, **ctx):
    ctx.setdefault('stations', [])
    ctx.setdefault('known_structures', [])
    ctx.setdefault('unknown_structures', [])
    ctx.setdefault('selected_location_id', None)
    ctx.setdefault('locations', [])
    with app.test_request_context('/'):
        return render_template('my_assets/show.html', title='My assets', **ctx)


def _asset(quantity=5, station_id=None, structure_id=None,
           is_blueprint_copy=None, location_flag=None, esi_item_id=None,
           parent_esi_item_id=None):
    return SimpleNamespace(
        quantity=quantity,
        universe_station_id=station_id,
        universe_structure_id=structure_id,
        is_blueprint_copy=is_blueprint_copy,
        location_flag=location_flag,
        esi_item_id=esi_item_id,
        parent_esi_item_id=parent_esi_item_id,
    )


def _item(name='Tritanium'):
    return SimpleNamespace(name=name)


class TestMyAssetsTemplate:
    def test_renders_empty_state(self, app, user):
        html = _render(app, user=user, locations=[])
        assert 'No assets.' in html

    def test_renders_location_header(self, app, user):
        locations = [{'label': 'Jita IV', 'groups': [
            {'container': None, 'rows': [(_asset(), _item('Tritanium Blueprint'))]}
        ]}]
        html = _render(app, user=user, locations=locations)
        assert 'Jita IV' in html
        assert 'Tritanium Blueprint' in html

    def test_renders_bpc_type(self, app, user):
        locations = [{'label': 'Jita', 'groups': [
            {'container': None, 'rows': [(_asset(is_blueprint_copy=True), _item())]}
        ]}]
        html = _render(app, user=user, locations=locations)
        assert 'BPC' in html

    def test_renders_bpo_type(self, app, user):
        locations = [{'label': 'Jita', 'groups': [
            {'container': None, 'rows': [(_asset(is_blueprint_copy=False), _item())]}
        ]}]
        html = _render(app, user=user, locations=locations)
        assert 'BPO' in html

    def test_renders_unknown_type(self, app, user):
        locations = [{'label': 'Jita', 'groups': [
            {'container': None, 'rows': [(_asset(is_blueprint_copy=None), _item())]}
        ]}]
        html = _render(app, user=user, locations=locations)
        assert '—' in html

    def test_renders_container_subheader(self, app, user):
        locations = [{'label': 'Jita', 'groups': [
            {'container': None, 'rows': [(_asset(), _item('Item A'))]},
            {'container': 'Giant Secure Can', 'rows': [(_asset(), _item('Item B'))]},
        ]}]
        html = _render(app, user=user, locations=locations)
        assert 'Giant Secure Can' in html
        assert 'Inside' in html
        assert 'Item A' in html
        assert 'Item B' in html

    def test_renders_multiple_locations(self, app, user):
        locations = [
            {'label': 'Jita IV', 'groups': [
                {'container': None, 'rows': [(_asset(), _item('Alpha'))]}
            ]},
            {'label': 'Amarr VIII', 'groups': [
                {'container': None, 'rows': [(_asset(), _item('Beta'))]}
            ]},
        ]
        html = _render(app, user=user, locations=locations)
        assert 'Jita IV' in html
        assert 'Amarr VIII' in html
        assert 'Alpha' in html
        assert 'Beta' in html

    def test_renders_location_filter_dropdown(self, app, db, user):
        from tests.factories import (
            make_universe_region, make_universe_constellation,
            make_universe_system, make_universe_station,
        )
        ur = make_universe_region(db, region_id=10000002)
        uc = make_universe_constellation(db, ur)
        us = make_universe_system(db, uc)
        st = make_universe_station(db, us)
        db.session.commit()
        html = _render(app, user=user, locations=[], stations=[st])
        assert 'Filter' in html
        assert st.name in html

    def test_unknown_structure_shown_in_dropdown(self, app, user):
        unknown = SimpleNamespace(name='ZZ-999', id=1_000_000_000_003)
        html = _render(app, user=user, locations=[], unknown_structures=[unknown])
        assert 'ZZ-999' in html
