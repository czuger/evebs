from datetime import datetime
from evebs.extensions import db


class Crontab(db.Model):
    __tablename__ = 'crontabs'

    id = db.Column(db.BigInteger, primary_key=True)
    cron_name = db.Column(db.String, nullable=False)
    status = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def start(cls, cron_name):
        import os
        if os.environ.get('FLASK_ENV') == 'development':
            return
        record = cls.query.filter_by(cron_name=str(cron_name)).first()
        if not record:
            record = cls(cron_name=str(cron_name), status=False)
            db.session.add(record)
        if record.status:
            print('Process actually running. Exiting')
            import sys
            sys.exit(0)
        record.status = True
        record.updated_at = datetime.utcnow()
        db.session.commit()

    @classmethod
    def stop(cls, cron_name):
        cls.query.filter_by(cron_name=str(cron_name)).update(
            {'status': False, 'updated_at': datetime.utcnow()}
        )
        db.session.commit()
