from datetime import datetime
from evebs.extensions import db


class Constant(db.Model):
    __tablename__ = 'constants'

    id = db.Column(db.BigInteger, primary_key=True)
    libe = db.Column(db.String, nullable=False, unique=True)
    f_value = db.Column(db.Float)
    description = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
