from datetime import datetime

from evebs.extensions import db


class BpcAsset(db.Model):
    __tablename__ = 'bpc_assets'

    id = db.Column(db.BigInteger, primary_key=True)
    universe_station_id = db.Column(db.BigInteger, db.ForeignKey('universe_stations.id'))
    universe_structure_id = db.Column(db.BigInteger)
    quantity = db.Column(db.BigInteger, nullable=False)
    location_flag = db.Column(db.String)
    location_type = db.Column(db.String)
    touched = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='bpc_assets')
