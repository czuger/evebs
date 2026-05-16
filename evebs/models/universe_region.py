from datetime import datetime
from evebs.extensions import db


class UniverseRegion(db.Model):
    __tablename__ = 'universe_regions'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)

    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    eve_market_histories_groups = db.relationship('EveMarketHistoriesGroup', back_populates='universe_region')
    universe_constellations = db.relationship('UniverseConstellation', back_populates='universe_region')
    trade_hubs = db.relationship('TradeHub', back_populates='universe_region')