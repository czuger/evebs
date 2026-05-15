from datetime import datetime
from evebs.extensions import db


class PricesAdvice(db.Model):
    __tablename__ = 'prices_advices'

    id = db.Column(db.Integer, primary_key=True)
    eve_item_id = db.Column(db.Integer, db.ForeignKey('eve_items.id'), nullable=False)
    trade_hub_id = db.Column(db.Integer, db.ForeignKey('trade_hubs.id'), nullable=False)
    vol_month = db.Column(db.BigInteger)
    avg_price_month = db.Column(db.Float)
    immediate_montly_pcent = db.Column(db.Float)
    margin_percent = db.Column(db.Float)
    avg_price_week = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eve_item = db.relationship('EveItem', back_populates='prices_advices')
    trade_hub = db.relationship('TradeHub', back_populates='prices_advices')
