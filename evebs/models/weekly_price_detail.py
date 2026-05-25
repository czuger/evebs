from datetime import datetime

from evebs.extensions import db


class WeeklyPriceDetail(db.Model):
    __tablename__ = 'weekly_price_details'

    __table_args__ = (
        db.UniqueConstraint('eve_item_id', 'trade_hub_id', 'day', name='uq_weekly_price_details_item_hub_day'),
    )

    id = db.Column(db.BigInteger, primary_key=True)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    trade_hub_id = db.Column(db.BigInteger, db.ForeignKey('trade_hubs.id'), nullable=False)
    day = db.Column(db.Date, nullable=False)
    volume = db.Column(db.Float, nullable=False)
    weighted_avg_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eve_item = db.relationship('EveItem', back_populates='weekly_price_details')
    trade_hub = db.relationship('TradeHub', back_populates='weekly_price_details')
