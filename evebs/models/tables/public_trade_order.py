from datetime import datetime

from evebs.extensions import db


class PublicTradeOrder(db.Model):
    __tablename__ = 'public_trade_orders'

    id = db.Column(db.BigInteger, primary_key=True)
    universe_system_id = db.Column(db.BigInteger, db.ForeignKey('universe_systems.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    order_id = db.Column(db.BigInteger, nullable=False, unique=True)
    is_buy_order = db.Column(db.Boolean, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    range = db.Column(db.String, nullable=False)
    volume_remain = db.Column(db.BigInteger, nullable=False)
    volume_total = db.Column(db.BigInteger, nullable=False)
    min_volume = db.Column(db.BigInteger, nullable=False)
    location_id = db.Column(db.BigInteger)
    touched = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    universe_system = db.relationship('UniverseSystem', back_populates='public_trade_orders')
    eve_item = db.relationship('EveItem', back_populates='public_trade_orders')
