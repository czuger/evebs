import json
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from evebs.extensions import db


class UniverseRegion(db.Model):
    __tablename__ = 'universe_regions'

    id = db.Column(db.BigInteger, primary_key=True)
    cpp_region_id = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    constellations = db.Column(ARRAY(db.Integer), default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eve_market_histories_groups = db.relationship('EveMarketHistoriesGroup', back_populates='universe_region')
    universe_constellations = db.relationship('UniverseConstellation', back_populates='universe_region')
    trade_hubs = db.relationship('TradeHub', back_populates='universe_region')