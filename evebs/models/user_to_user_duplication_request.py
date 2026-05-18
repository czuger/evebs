from datetime import datetime
from evebs.extensions import db


class UserToUserDuplicationRequest(db.Model):
    """Request to copy one user's settings or items to another user."""

    __tablename__ = 'user_to_user_duplication_requests'

    id = db.Column(db.BigInteger, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    duplication_type = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])
