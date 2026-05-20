from datetime import datetime
from sqlalchemy import UniqueConstraint
from evebs.extensions import db


class BuyOrdersAnalytic(db.Model):
    """Computed buy-order margin analysis for an item at a trade hub."""

    __tablename__ = 'buy_orders_analytics'
    __table_args__ = (UniqueConstraint('system_id', 'eve_item_id'),)

    id = db.Column(db.BigInteger, primary_key=True)
    system_id = db.Column(db.BigInteger, db.ForeignKey('universe_systems.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('universe_types.id'), nullable=False)
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

    universe_system = db.relationship('UniverseSystem')
    eve_item = db.relationship('UniverseType', primaryjoin='BuyOrdersAnalytic.eve_item_id == UniverseType.id', foreign_keys='[BuyOrdersAnalytic.eve_item_id]', viewonly=True)
