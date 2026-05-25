import os
import sys
from datetime import datetime, timedelta

import pytest

# Must be set before any project import so config.py picks up the test database.
os.environ['EVEBS_TEST_DB'] = '1'

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from sqlalchemy import text

from evebs import create_app
from evebs.extensions import db as _db


def truncate_all_tables(db):
    """Truncate every real table. TRUNCATE … CASCADE on PostgreSQL, DELETE on SQLite."""
    tables = [t for t in db.metadata.sorted_tables if not t.info.get('is_view')]
    if not tables:
        return
    if db.engine.dialect.name == 'postgresql':
        names = ', '.join(f'"{t.name}"' for t in tables)
        db.session.execute(text(f'TRUNCATE {names} RESTART IDENTITY CASCADE'))
    else:
        for table in reversed(tables):
            db.session.execute(table.delete())
    db.session.commit()


@pytest.fixture(scope='session')
def app():
    _app = create_app()
    _app.config['TESTING'] = True
    with _app.app_context():
        yield _app


@pytest.fixture(autouse=True)
def _truncate(app):
    with app.app_context():
        truncate_all_tables(_db)
    yield


@pytest.fixture
def db(app, _truncate):
    """Open app context with a clean session for direct DB access."""
    with app.app_context():
        yield _db
        _db.session.rollback()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(db):
    from evebs.models import User
    u = User(
        uid='123456789',
        name='Test Pilot',
        provider='eve_online_sso',
        token='tok_test',
        renew_token='refresh_test',
        expires_on=datetime.utcnow() + timedelta(hours=1),
        initialization_finalized=True,
    )
    db.session.add(u)
    db.session.commit()
    db.session.refresh(u)
    return u


@pytest.fixture
def admin_user(db):
    from evebs.models import User
    u = User(
        uid='987654321',
        name='Admin Pilot',
        provider='eve_online_sso',
        token='tok_admin',
        renew_token='refresh_admin',
        expires_on=datetime.utcnow() + timedelta(hours=1),
        admin=True,
        initialization_finalized=True,
    )
    db.session.add(u)
    db.session.commit()
    db.session.refresh(u)
    return u


def _log_in(client, user_id):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user_id)
        sess['_fresh'] = True


@pytest.fixture
def auth_client(client, user):
    """Test client logged in as a regular user. Returns (client, user)."""
    _log_in(client, user.id)
    return client, user


@pytest.fixture
def admin_client(client, admin_user):
    """Test client logged in as an admin. Returns (client, admin_user)."""
    _log_in(client, admin_user.id)
    return client, admin_user
