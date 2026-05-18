from datetime import datetime
from evebs.extensions import db


class BpcAsset(db.Model):
    """A single item in the user's in-game asset inventory, optionally located at a station."""

    __tablename__ = 'bpc_assets'

    id = db.Column(db.BigInteger, primary_key=True)
    universe_station_id = db.Column(db.BigInteger, db.ForeignKey('universe_stations.id'))
    quantity = db.Column(db.BigInteger, nullable=False)
    touched = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('universe_types.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='bpc_assets')
    universe_type = db.relationship('UniverseType')
    universe_station = db.relationship('UniverseStation')
