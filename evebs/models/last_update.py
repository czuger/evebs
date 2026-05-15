from datetime import datetime
from evebs.extensions import db


class LastUpdate(db.Model):
    __tablename__ = 'last_updates'

    id = db.Column(db.BigInteger, primary_key=True)
    update_type = db.Column(db.String, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    def set(cls, update_type):
        record = cls.query.filter_by(update_type=str(update_type)).first()
        if record:
            record.updated_at = datetime.utcnow()
        else:
            record = cls(update_type=str(update_type), updated_at=datetime.utcnow())
            db.session.add(record)
        db.session.commit()
