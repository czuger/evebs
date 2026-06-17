from datetime import datetime

from evebs.extensions import db


class TradeRouteBuy(db.Model):
    """A user's saved inter-hub buy: an item to buy at src_hub and sell at dst_hub,
    with a planned quantity. One entry per (user, item, src_hub, dst_hub)."""
    __tablename__ = 'trade_route_buys'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'eve_item_id', 'src_hub_id', 'dst_hub_id',
                            name='uq_trade_route_buys_user_item_route'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    src_hub_id = db.Column(db.Integer, db.ForeignKey('universe_systems.id'), nullable=False)
    dst_hub_id = db.Column(db.Integer, db.ForeignKey('universe_systems.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='trade_route_buys')
    eve_item = db.relationship('EveItem', foreign_keys=[eve_item_id])
    src_hub = db.relationship('UniverseSystem', foreign_keys=[src_hub_id])
    dst_hub = db.relationship('UniverseSystem', foreign_keys=[dst_hub_id])
