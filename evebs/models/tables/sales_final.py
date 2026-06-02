from datetime import datetime

from evebs.extensions import db


class SalesFinal(db.Model):
    __tablename__ = 'sales_finals'

    id = db.Column(db.BigInteger, primary_key=True)
    day = db.Column(db.Date, nullable=False)
    universe_system_id = db.Column(db.Integer, db.ForeignKey('universe_systems.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    volume = db.Column(db.BigInteger, nullable=False)
    price = db.Column(db.Float, nullable=False)
    order_id = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    universe_system = db.relationship('UniverseSystem', back_populates='sales_finals')
    eve_item = db.relationship('EveItem', back_populates='sales_finals')
