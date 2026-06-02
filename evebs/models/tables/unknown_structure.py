from datetime import datetime

from evebs.extensions import db


class UnknownStructure(db.Model):
    __tablename__ = 'unknown_structures'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
