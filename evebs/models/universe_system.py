from datetime import datetime
from evebs.extensions import db


class UniverseSystem(db.Model):
    __tablename__ = 'universe_systems'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    star_id = db.Column(db.BigInteger, nullable=False)

    universe_constellation_id = db.Column(db.BigInteger, db.ForeignKey('universe_constellations.id'))

    name = db.Column(db.Text, nullable=False)

    security_class = db.Column(db.Text, nullable=False)
    security_status = db.Column(db.Float, nullable=False)

    trade_hub = db.Column(db.Boolean, nullable=False, default=False)
    kill_stats_current_month = db.Column(db.Integer, nullable=True)
    kill_stats_last_month = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    universe_constellation = db.relationship('UniverseConstellation', back_populates='universe_systems')
    structures = db.relationship('Structure', back_populates='universe_system')
    universe_stations = db.relationship('UniverseStation', back_populates='universe_system')
