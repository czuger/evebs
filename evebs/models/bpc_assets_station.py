from datetime import datetime
from evebs.extensions import db


class BpcAssetsStation(db.Model):
    """Station the user has marked as a container for their BPC assets."""

    __tablename__ = 'bpc_assets_stations'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    universe_station_id = db.Column(db.BigInteger, db.ForeignKey('universe_stations.id'), nullable=False)
    touched = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='bpc_assets_stations')
    universe_station = db.relationship('UniverseStation')
