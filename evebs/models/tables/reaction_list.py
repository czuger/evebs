from datetime import datetime

from evebs.extensions import db


class ReactionList(db.Model):
    """A user's planned reaction runs. Unlike ProductionList there is no trade-hub —
    reactions are location-agnostic here (the reaction job tax is a flat per-user value
    in User.reaction_modifications)."""
    __tablename__ = 'reaction_lists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    runs_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='reaction_lists')
    eve_item = db.relationship('EveItem')
