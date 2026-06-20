from datetime import UTC, datetime

from evebs.extensions import db


class LastViewedItem(db.Model):
    """One row per (user, item) the user has opened on items#show. `view_count` is bumped
    on each view; the unique constraint enforces one row per (user, item)."""
    __tablename__ = 'user_last_viewed_items'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'eve_item_id', name='uq_user_last_viewed_items_user_item'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    view_count = db.Column(db.Integer, default=1, nullable=False)
    viewed_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC),
                          onupdate=lambda: datetime.now(UTC), nullable=False)

    user = db.relationship('User', back_populates='last_viewed_items')
    eve_item = db.relationship('EveItem')
