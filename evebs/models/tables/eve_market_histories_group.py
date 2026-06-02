from datetime import datetime

from evebs.extensions import db


class EveMarketHistoriesGroup(db.Model):
    __tablename__ = 'eve_market_histories_groups'

    id = db.Column(db.BigInteger, primary_key=True)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    volume = db.Column(db.BigInteger, nullable=False)
    highest = db.Column(db.Float)
    lowest = db.Column(db.Float)
    average = db.Column(db.Float)
    universe_region_id = db.Column(db.Integer, db.ForeignKey('universe_regions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eve_item = db.relationship('EveItem', back_populates='eve_market_histories_groups')
    universe_region = db.relationship('UniverseRegion', back_populates='eve_market_histories_groups')
