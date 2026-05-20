from datetime import datetime
from evebs.extensions import db


class SalesFinal(db.Model):
    """Completed sale event recorded when a sell order's volume decreases or expires."""

    __tablename__ = 'sales_finals'

    id = db.Column(db.BigInteger, primary_key=True)
    day = db.Column(db.Date, nullable=False)
    system_id = db.Column(db.BigInteger, db.ForeignKey('universe_systems.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('universe_types.id'), nullable=False)
    volume = db.Column(db.BigInteger, nullable=False)
    price = db.Column(db.Float, nullable=False)
    order_id = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    universe_system = db.relationship('UniverseSystem')
    eve_item = db.relationship('UniverseType', primaryjoin='SalesFinal.eve_item_id == UniverseType.id', foreign_keys='[SalesFinal.eve_item_id]', viewonly=True)
