from datetime import datetime
from evebs.extensions import db


class PublicTradeOrder(db.Model):
    __tablename__ = 'public_trade_orders'

    id = db.Column(db.BigInteger, primary_key=True)
    trade_hub_id = db.Column(db.BigInteger, db.ForeignKey('trade_hubs.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('universe_types.id'), nullable=False)
    order_id = db.Column(db.BigInteger, nullable=False, unique=True)
    is_buy_order = db.Column(db.Boolean, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    range = db.Column(db.String, nullable=False)
    volume_remain = db.Column(db.BigInteger, nullable=False)
    volume_total = db.Column(db.BigInteger, nullable=False)
    min_volume = db.Column(db.BigInteger, nullable=False)
    touched = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trade_hub = db.relationship('TradeHub', back_populates='public_trade_orders')
    eve_item = db.relationship('UniverseType', primaryjoin='PublicTradeOrder.eve_item_id == UniverseType.id', foreign_keys='[PublicTradeOrder.eve_item_id]', viewonly=True)
