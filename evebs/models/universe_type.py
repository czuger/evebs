from evebs.extensions import db


class UniverseType(db.Model):
    """An in-game item type from the Eve universe hierarchy."""

    __tablename__ = 'universe_types'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)  # called type_id in the fetch request
    capacity = db.Column(db.Float)
    description = db.Column(db.Text, nullable=False)
    graphic_id = db.Column(db.BigInteger)
    group_id = db.Column(db.BigInteger, db.ForeignKey('universe_groups.id'), nullable=False)
    icon_id = db.Column(db.BigInteger)
    market_group_id = db.Column(db.BigInteger, db.ForeignKey('market_groups.id'))
    mass = db.Column(db.Float)
    name = db.Column(db.Text, nullable=False)
    packaged_volume = db.Column(db.Float)
    portion_size = db.Column(db.BigInteger)
    published = db.Column(db.Boolean, nullable=False)
    radius = db.Column(db.Float)
    volume = db.Column(db.Float)

    universe_group = db.relationship('UniverseGroup', back_populates='universe_types')
    market_group = db.relationship('MarketGroup', back_populates='universe_types')
    market_orders = db.relationship('MarketOrder', back_populates='universe_type')
    blueprint = db.relationship('Blueprint', primaryjoin='UniverseType.id == Blueprint.produced_type_id', foreign_keys='[Blueprint.produced_type_id]', uselist=False, viewonly=True)

    @classmethod
    def find_by_slug(cls, slug):
        """Look up a type by numeric slug string; returns None on invalid input."""
        try:
            return cls.query.get(int(slug))
        except (ValueError, TypeError):
            return None
