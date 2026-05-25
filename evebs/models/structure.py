from datetime import datetime

from evebs.extensions import db


class Structure(db.Model):
    __tablename__ = 'structures'

    id = db.Column(db.BigInteger, primary_key=True)
    cpp_structure_id = db.Column(db.BigInteger, nullable=False, unique=True)
    forbidden = db.Column(db.Boolean, default=True, nullable=False)
    universe_system_id = db.Column(db.BigInteger, db.ForeignKey('universe_systems.id'))
    orders_count_pages = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    universe_system = db.relationship('UniverseSystem', back_populates='structures')
