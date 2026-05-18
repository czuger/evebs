from evebs.extensions import db


class MarketOrder(db.Model):
    """Live public market order fetched from ESI, linked to a system and item type."""

    __tablename__ = 'market_orders'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)  # called order_id in the fetch request
    duration = db.Column(db.BigInteger, nullable=False)
    is_buy_order = db.Column(db.Boolean, nullable=False)
    issued = db.Column(db.DateTime, nullable=False)
    location_id = db.Column(db.BigInteger, nullable=False)  # do not link
    min_volume = db.Column(db.BigInteger, nullable=False)
    price = db.Column(db.Float, nullable=False)
    range = db.Column(db.Text, nullable=False)
    system_id = db.Column(db.BigInteger, db.ForeignKey('universe_systems.id'), nullable=False)
    type_id = db.Column(db.BigInteger, db.ForeignKey('universe_types.id'), nullable=False)
    volume_remain = db.Column(db.BigInteger, nullable=False)
    volume_total = db.Column(db.BigInteger)
    source = db.Column(db.Enum('list_order_in_a_region', 'list_order_in_a_structure', name='market_order_source'), nullable=False)

    universe_system = db.relationship('UniverseSystem', back_populates='market_orders')
    universe_type = db.relationship('UniverseType', back_populates='market_orders')
