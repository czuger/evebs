from datetime import datetime
from evebs.extensions import db


class Blueprint(db.Model):
    """Manufacturing blueprint: links a produced item to its required materials and run parameters."""

    __tablename__ = 'blueprints'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    produced_type_id = db.Column(db.BigInteger, db.ForeignKey('universe_types.id'), nullable=False, unique=True)
    nb_runs = db.Column(db.Integer, nullable=False)
    prod_qtt = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    universe_type = db.relationship('UniverseType', primaryjoin='Blueprint.produced_type_id == UniverseType.id', foreign_keys='[Blueprint.produced_type_id]', uselist=False, viewonly=True)
    blueprint_materials = db.relationship('BlueprintMaterial', back_populates='blueprint', cascade='all, delete-orphan')
    blueprint_modifications = db.relationship('BlueprintModification', back_populates='blueprint')

    @property
    def batch_elements_count(self):
        """Total units produced across all runs (prod_qtt × nb_runs)."""
        return self.prod_qtt * self.nb_runs
