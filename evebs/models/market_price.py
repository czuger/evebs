from evebs.extensions import db


class MarketPrice(db.Model):
    """ESI-provided adjusted and average price for a universe type."""

    __tablename__ = 'market_prices'

    __table_args__ = (db.Index('ix_market_prices_type_id', 'type_id', unique=True),)

    id = db.Column(db.BigInteger, primary_key=True)
    type_id = db.Column(db.BigInteger, db.ForeignKey('universe_types.id'), nullable=False)
    adjusted_price = db.Column(db.Float)
    average_price = db.Column(db.Float)

    universe_type = db.relationship('UniverseType')
