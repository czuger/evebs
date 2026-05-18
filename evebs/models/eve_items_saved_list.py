import json
from datetime import datetime
from evebs.extensions import db


class EveItemsSavedList(db.Model):
    """Snapshot of a user's tracked item selection, stored as a JSON id list."""

    __tablename__ = 'eve_items_saved_lists'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String, nullable=False)
    saved_ids = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='eve_items_saved_lists')

    def get_ids(self):
        """Deserialise the saved item IDs from JSON."""
        return json.loads(self.saved_ids)

    def set_ids(self, ids):
        """Serialise a list of item IDs to JSON and store it."""
        self.saved_ids = json.dumps(ids)
