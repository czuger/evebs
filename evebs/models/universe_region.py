import json
from datetime import datetime

from evebs.extensions import db


class UniverseRegion(db.Model):
    __tablename__ = 'universe_regions'

    id = db.Column(db.BigInteger, primary_key=True)
    cpp_region_id = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    orders_pages_count = db.Column(db.Integer, default=0, nullable=False)
    _market_items = db.Column('market_items', db.Text, default='[]', nullable=False)
    market_items_count = db.Column(db.Integer, default=0, nullable=False)
    download_process_id = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eve_market_histories_groups = db.relationship('EveMarketHistoriesGroup', back_populates='universe_region')
    universe_constellations = db.relationship('UniverseConstellation', back_populates='universe_region')

    @property
    def market_items(self):
        return json.loads(self._market_items or '[]')

    @market_items.setter
    def market_items(self, value):
        self._market_items = json.dumps(value)
