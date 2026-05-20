from evebs.extensions import db


class MarketSellerPrice(db.Model):
    """Volume-weighted sell price percentiles per (type, system) — materialized view."""

    __tablename__ = 'market_seller_prices'
    __table_args__ = {'info': {'is_view': True}}

    type_id = db.Column(db.BigInteger, db.ForeignKey('universe_types.id'), primary_key=True)
    system_id = db.Column(db.BigInteger, db.ForeignKey('universe_systems.id'), primary_key=True)
    p5_price = db.Column(db.Float)
    p10_price = db.Column(db.Float)
    p20_price = db.Column(db.Float)
    p80_price = db.Column(db.Float)
    p90_price = db.Column(db.Float)
    p95_price = db.Column(db.Float)
    volume = db.Column(db.BigInteger)

    universe_type = db.relationship('UniverseType')
    universe_system = db.relationship('UniverseSystem')
