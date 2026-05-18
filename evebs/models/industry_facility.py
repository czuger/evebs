from evebs.extensions import db


class IndustryFacility(db.Model):
    """An industry-capable facility (NPC station or player structure) from ESI /industry/facilities/."""

    __tablename__ = 'industry_facilities'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)  # ESI facility_id
    universe_system_id = db.Column(db.BigInteger, db.ForeignKey('universe_systems.id'), nullable=False)
    universe_station_id = db.Column(db.BigInteger, db.ForeignKey('universe_stations.id'), nullable=True)
    owner_id = db.Column(db.BigInteger, nullable=False)
    type_id = db.Column(db.BigInteger, nullable=False)
    tax = db.Column(db.Float, nullable=True)

    universe_system = db.relationship('UniverseSystem')
    universe_station = db.relationship('UniverseStation')
