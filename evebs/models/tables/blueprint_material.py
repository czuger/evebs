from datetime import datetime

from evebs.extensions import db


class BlueprintMaterial(db.Model):
    __tablename__ = 'blueprint_materials'

    id = db.Column(db.Integer, primary_key=True)
    blueprint_id = db.Column(db.Integer, db.ForeignKey('blueprints.id'), nullable=False, index=True)
    required_qtt = db.Column(db.Integer, nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    blueprint = db.relationship('Blueprint', back_populates='blueprint_materials')
    eve_item = db.relationship('EveItem', foreign_keys=[eve_item_id], back_populates='blueprint_materials')
