from evebs.extensions import db


class PricesMin(db.Model):
    __tablename__ = 'prices_mins'
    __table_args__ = (
        db.UniqueConstraint('universe_system_id', 'eve_item_id', name='uq_prices_mins_hub_item'),
    )

    id = db.Column(db.Integer, primary_key=True)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'))
    universe_system_id = db.Column(db.BigInteger, db.ForeignKey('universe_systems.id'))
    min_price = db.Column(db.Float)
    volume = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    eve_item = db.relationship('EveItem', back_populates='prices_mins')
    universe_system = db.relationship('UniverseSystem', back_populates='prices_mins')
