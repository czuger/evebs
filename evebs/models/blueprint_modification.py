from datetime import datetime
from evebs.extensions import db


class BlueprintModification(db.Model):
    """Per-user percentage adjustment applied to a blueprint's cost calculation."""

    __tablename__ = 'blueprint_modifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    blueprint_id = db.Column(db.BigInteger, db.ForeignKey('blueprints.id'), nullable=False)
    percent_modification_value = db.Column(db.Float, nullable=False)
    touched = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='blueprint_modifications')
    blueprint = db.relationship('Blueprint', back_populates='blueprint_modifications')
