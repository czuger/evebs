import pytest
from evebs import create_app
from evebs.extensions import db as _db
from evebs.models import UniverseRegion, UniverseConstellation, UniverseSystem, UniverseStation
from config import TestConfig


@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(autouse=True)
def clean_tables(app):
    yield
    with app.app_context():
        _db.session.query(UniverseStation).delete()
        _db.session.query(UniverseSystem).delete()
        _db.session.query(UniverseConstellation).delete()
        _db.session.query(UniverseRegion).delete()
        _db.session.commit()
