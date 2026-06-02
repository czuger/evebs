import threading
import pytest
from werkzeug.serving import make_server

from tests.factories import make_market_group, make_item


@pytest.fixture(scope='session')
def live_server_url(app):
    srv = make_server('127.0.0.1', 5099, app)
    t = threading.Thread(target=srv.serve_forever)
    t.daemon = True
    t.start()
    yield 'http://127.0.0.1:5099'
    srv.shutdown()


@pytest.fixture
def auth_page(page, app, user, live_server_url):
    """Playwright page pre-authenticated as `user` via session cookie injection."""
    page.goto(live_server_url + '/')
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        c.get('/')
        cookie = c.get_cookie('session')
        if cookie:
            page.context.add_cookies([{
                'name': 'session',
                'value': cookie.value,
                'domain': '127.0.0.1',
                'path': '/',
            }])
    yield page


@pytest.fixture
def root_group(db):
    grp = make_market_group(db, group_id=100, name='Ships')
    db.session.commit()
    return grp


@pytest.fixture
def leaf_group(db, root_group):
    grp = make_market_group(db, group_id=101, name='Frigates', parent=root_group)
    db.session.commit()
    return grp


@pytest.fixture
def eve_item(db, leaf_group):
    item = make_item(db, item_id=582, name='Rifter', slug='rifter',
                     market_group=leaf_group)
    db.session.commit()
    return item
