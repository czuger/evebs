from evebs.extensions import db


class Station(db.Model):
    __tablename__ = 'stations'

    id = db.Column(db.Integer, primary_key=True)
    trade_hub_id = db.Column(db.Integer, db.ForeignKey('trade_hubs.id'))
    name = db.Column(db.String)
    cpp_station_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    trade_hub = db.relationship('TradeHub', back_populates='stations')

    @classmethod
    def to_trade_hub_id(cls, location_id):
        station = cls.query.filter_by(cpp_station_id=location_id).first()
        return station.trade_hub_id if station else None
