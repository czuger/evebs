from evebs.extensions import db


class MarketBuyerPrice(db.Model):
    """Max/avg/median buy prices per (type, system) from market_orders materialized view."""

    __tablename__ = 'market_buyer_prices'
    __table_args__ = {'info': {'is_view': True}}

    type_id = db.Column(db.BigInteger, db.ForeignKey('universe_types.id'), primary_key=True)
    system_id = db.Column(db.BigInteger, db.ForeignKey('universe_systems.id'), primary_key=True)
    p90_price = db.Column(db.Float)
    volume = db.Column(db.BigInteger)

    universe_type = db.relationship('UniverseType')
    universe_system = db.relationship('UniverseSystem')
