from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from evebs.extensions import db


class UniverseStation(db.Model):
    __tablename__ = 'universe_stations'

    id = db.Column(db.BigInteger, primary_key=True)

    cpp_station_id = db.Column(db.BigInteger, nullable=False, unique=True)
    cpp_owner_id = db.Column(db.BigInteger, nullable=False)

    universe_system_id = db.Column(db.BigInteger, db.ForeignKey('universe_systems.id'), nullable=False)

    name = db.Column(db.String, nullable=False)
    office_rental_cost = db.Column(db.Float, nullable=False)
    reprocessing_efficiency = db.Column(db.Float, nullable=False)
    reprocessing_stations_take = db.Column(db.Float, nullable=False)

    services = db.Column('services', ARRAY(db.String), nullable=False, default=[])

    security_status = db.Column(db.Float)
    jita_distance = db.Column(db.Integer)
    industry_costs_indices = db.Column('industry_costs_indices', db.JSON)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    universe_system = db.relationship('UniverseSystem', back_populates='universe_stations')