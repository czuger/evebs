import json
from datetime import datetime

from evebs.extensions import db


class UniverseStation(db.Model):
    __tablename__ = 'universe_stations'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    name = db.Column(db.String, nullable=False)
    _services = db.Column('services', db.Text, nullable=False, default='[]')
    office_rental_cost = db.Column(db.Float, nullable=False)
    security_status = db.Column(db.Float)
    jita_distance = db.Column(db.Integer)
    _industry_costs_indices = db.Column('industry_costs_indices', db.Text)
    universe_system_id = db.Column(db.Integer, db.ForeignKey('universe_systems.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    universe_system = db.relationship('UniverseSystem', back_populates='universe_stations')

    @property
    def services(self):
        return json.loads(self._services or '[]')

    @services.setter
    def services(self, value):
        self._services = json.dumps(value)

    @property
    def industry_costs_indices(self):
        return json.loads(self._industry_costs_indices or '{}') if self._industry_costs_indices else {}

    @industry_costs_indices.setter
    def industry_costs_indices(self, value):
        self._industry_costs_indices = json.dumps(value) if value else None
