from datetime import datetime

from evebs.extensions import db


class UserSaleOrder(db.Model):
    __tablename__ = 'user_sale_orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    universe_system_id = db.Column(db.BigInteger, db.ForeignKey('universe_systems.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='user_sale_orders')
    eve_item = db.relationship('EveItem')
    universe_system = db.relationship('UniverseSystem', back_populates='user_sale_orders')
