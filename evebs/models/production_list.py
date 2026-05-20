from datetime import datetime
from evebs.extensions import db


class ProductionList(db.Model):
    """An item the user wants to craft, with a target run count at a specific hub."""

    __tablename__ = 'production_lists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    system_id = db.Column(db.Integer, db.ForeignKey('universe_systems.id'), nullable=False)
    eve_item_id = db.Column(db.Integer, db.ForeignKey('universe_types.id'), nullable=False)
    runs_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='production_lists')
    universe_system = db.relationship('UniverseSystem')
    eve_item = db.relationship('UniverseType', primaryjoin='ProductionList.eve_item_id == UniverseType.id', foreign_keys='[ProductionList.eve_item_id]', viewonly=True)
