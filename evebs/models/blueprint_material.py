from datetime import datetime
from evebs.extensions import db


class BlueprintMaterial(db.Model):
    """Material required by a blueprint, with the quantity needed per run."""

    __tablename__ = 'blueprint_materials'

    id = db.Column(db.BigInteger, primary_key=True)
    blueprint_id = db.Column(db.BigInteger, db.ForeignKey('blueprints.id'), nullable=False)
    required_qtt = db.Column(db.BigInteger, nullable=False)
    universe_type_id = db.Column(db.BigInteger, db.ForeignKey('universe_types.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    blueprint = db.relationship('Blueprint', back_populates='blueprint_materials')
    universe_type = db.relationship('UniverseType', primaryjoin='BlueprintMaterial.universe_type_id == UniverseType.id', foreign_keys='[BlueprintMaterial.universe_type_id]', viewonly=True)
