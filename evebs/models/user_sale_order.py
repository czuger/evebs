from datetime import datetime
from evebs.extensions import db


class UserSaleOrder(db.Model):
    __tablename__ = 'user_sale_orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    eve_item_id = db.Column(db.Integer, db.ForeignKey('universe_types.id'), nullable=False)
    trade_hub_id = db.Column(db.Integer, db.ForeignKey('trade_hubs.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='user_sale_orders')
    eve_item = db.relationship('UniverseType', primaryjoin='UserSaleOrder.eve_item_id == UniverseType.id', foreign_keys='[UserSaleOrder.eve_item_id]', viewonly=True)
    trade_hub = db.relationship('TradeHub', back_populates='user_sale_orders')
