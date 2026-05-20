from datetime import datetime
from sqlalchemy import UniqueConstraint
from evebs.extensions import db


class WeeklyPriceDetail(db.Model):
    """Daily volume-weighted average price for an item at a hub (7-day rolling window)."""

    __tablename__ = 'weekly_price_details'
    __table_args__ = (UniqueConstraint('eve_item_id', 'system_id', 'day'),)

    id = db.Column(db.BigInteger, primary_key=True)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('universe_types.id'), nullable=False)
    system_id = db.Column(db.BigInteger, db.ForeignKey('universe_systems.id'), nullable=False)
    day = db.Column(db.Date, nullable=False)
    volume = db.Column(db.Float, nullable=False)
    weighted_avg_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eve_item = db.relationship('UniverseType', primaryjoin='WeeklyPriceDetail.eve_item_id == UniverseType.id', foreign_keys='[WeeklyPriceDetail.eve_item_id]', viewonly=True)
    universe_system = db.relationship('UniverseSystem')
