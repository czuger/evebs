from datetime import datetime
from evebs.extensions import db


class UniverseConstellation(db.Model):
    __tablename__ = 'universe_constellations'

    id = db.Column(db.BigInteger, primary_key=True)
    cpp_constellation_id = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    universe_region_id = db.Column(db.BigInteger, db.ForeignKey('universe_regions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    universe_region = db.relationship('UniverseRegion', back_populates='universe_constellations')
    universe_systems = db.relationship('UniverseSystem', back_populates='universe_constellation')
