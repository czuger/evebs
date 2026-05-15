from datetime import datetime
from evebs.extensions import db


class BuyOrdersAnalytic(db.Model):
    __tablename__ = 'buy_orders_analytics'

    id = db.Column(db.BigInteger, primary_key=True)
    trade_hub_id = db.Column(db.BigInteger, db.ForeignKey('trade_hubs.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    approx_max_price = db.Column(db.Float)
    over_approx_max_price_volume = db.Column(db.BigInteger)
    single_unit_cost = db.Column(db.Float)
    single_unit_margin = db.Column(db.Float)
    estimated_volume_margin = db.Column(db.Float)
    per_job_margin = db.Column(db.Float)
    per_job_run_margin = db.Column(db.Float)
    final_margin = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trade_hub = db.relationship('TradeHub', back_populates='buy_orders_analytics')
    eve_item = db.relationship('EveItem', back_populates='buy_orders_analytics')
