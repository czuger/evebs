from datetime import datetime
from sqlalchemy import UniqueConstraint
from evebs.extensions import db


class PricesAdvice(db.Model):
    __tablename__ = 'prices_advices'
    __table_args__ = (UniqueConstraint('eve_item_id', 'trade_hub_id'),)

    id = db.Column(db.Integer, primary_key=True)
    eve_item_id = db.Column(db.Integer, db.ForeignKey('universe_types.id'), nullable=False)
    trade_hub_id = db.Column(db.Integer, db.ForeignKey('trade_hubs.id'), nullable=False)
    vol_month = db.Column(db.BigInteger)
    avg_price_month = db.Column(db.Float)
    immediate_montly_pcent = db.Column(db.Float)
    margin_percent = db.Column(db.Float)
    avg_price_week = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eve_item = db.relationship('UniverseType', primaryjoin='PricesAdvice.eve_item_id == UniverseType.id', foreign_keys='[PricesAdvice.eve_item_id]', viewonly=True)
    trade_hub = db.relationship('TradeHub', back_populates='prices_advices')
