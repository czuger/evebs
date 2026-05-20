from evebs.extensions import db


class MarketSellerPrice(db.Model):
    """Min/avg/median sell prices per (type, system) from market_orders materialized view."""

    __tablename__ = 'market_seller_prices'
    __table_args__ = {'info': {'is_view': True}}

    type_id = db.Column(db.BigInteger, db.ForeignKey('universe_types.id'), primary_key=True)
    system_id = db.Column(db.BigInteger, db.ForeignKey('universe_systems.id'), primary_key=True)
    p10_price = db.Column(db.Float)
    volume = db.Column(db.BigInteger)

    universe_type = db.relationship('UniverseType')
    universe_system = db.relationship('UniverseSystem')
