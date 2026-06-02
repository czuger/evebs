from datetime import datetime

from evebs.extensions import db


class UniverseStructure(db.Model):
    __tablename__ = 'universe_structures'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    name = db.Column(db.String, nullable=False)
    owner_id = db.Column(db.Integer, nullable=False)
    type_id = db.Column(db.Integer)
    universe_system_id = db.Column(db.Integer, db.ForeignKey('universe_systems.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    universe_system = db.relationship('UniverseSystem', back_populates='universe_structures')
