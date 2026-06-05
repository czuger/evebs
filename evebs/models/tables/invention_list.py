from datetime import datetime

from evebs.extensions import db


class InventionList(db.Model):
    __tablename__ = 'invention_lists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    universe_system_id = db.Column(db.Integer, db.ForeignKey('universe_systems.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    runs_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='invention_lists')
    universe_system = db.relationship('UniverseSystem', back_populates='invention_lists')
    eve_item = db.relationship('EveItem')
