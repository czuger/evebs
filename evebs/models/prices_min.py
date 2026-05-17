from sqlalchemy import UniqueConstraint
from evebs.extensions import db


class PricesMin(db.Model):
    __tablename__ = 'prices_mins'
    __table_args__ = (UniqueConstraint('trade_hub_id', 'eve_item_id'),)

    id = db.Column(db.Integer, primary_key=True)
    eve_item_id = db.Column(db.Integer, db.ForeignKey('universe_types.id'))
    trade_hub_id = db.Column(db.Integer, db.ForeignKey('trade_hubs.id'))
    min_price = db.Column(db.Float)
    volume = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    eve_item = db.relationship('UniverseType', primaryjoin='PricesMin.eve_item_id == UniverseType.id', foreign_keys='[PricesMin.eve_item_id]', viewonly=True)
    trade_hub = db.relationship('TradeHub', back_populates='prices_mins')
