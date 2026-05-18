from datetime import datetime
from evebs.extensions import db


class UniverseConstellation(db.Model):
    """A constellation grouping several solar systems within a region."""

    __tablename__ = 'universe_constellations'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    universe_region_id = db.Column(db.BigInteger, db.ForeignKey('universe_regions.id'), nullable=False)

    name = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    universe_region = db.relationship('UniverseRegion', back_populates='universe_constellations')
    universe_systems = db.relationship('UniverseSystem', back_populates='universe_constellation')
