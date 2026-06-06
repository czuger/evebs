from datetime import datetime

from evebs.extensions import db

ACTIVITY_LABELS = {
    1: 'Manufacturing',
    3: 'TE Research',
    4: 'ME Research',
    5: 'Copying',
    8: 'Invention',
    9: 'Reaction',
}


class IndustryJob(db.Model):
    __tablename__ = 'industry_jobs'

    id                     = db.Column(db.Integer, primary_key=True)
    user_id                = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    job_id                 = db.Column(db.BigInteger, nullable=False)
    installer_id           = db.Column(db.BigInteger)
    facility_id            = db.Column(db.BigInteger)
    station_id             = db.Column(db.BigInteger)
    activity_id            = db.Column(db.Integer, nullable=False)
    blueprint_id           = db.Column(db.BigInteger)
    blueprint_type_id      = db.Column(db.Integer)
    blueprint_location_id  = db.Column(db.BigInteger)
    output_location_id     = db.Column(db.BigInteger)
    runs                   = db.Column(db.Integer)
    cost                   = db.Column(db.Float)
    licensed_runs          = db.Column(db.Integer)
    probability            = db.Column(db.Float)
    product_type_id        = db.Column(db.Integer)
    status                 = db.Column(db.String, nullable=False)
    duration               = db.Column(db.Integer)
    start_date             = db.Column(db.DateTime)
    end_date               = db.Column(db.DateTime)
    pause_date             = db.Column(db.DateTime)
    completed_date         = db.Column(db.DateTime)
    completed_character_id = db.Column(db.BigInteger)
    successful_runs        = db.Column(db.Integer)
    created_at             = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at             = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='industry_jobs')
