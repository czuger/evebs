from evebs.extensions import db


class IndustryInterestingItem(db.Model):
    __tablename__ = 'industry_interesting_items'
    __table_args__ = (db.UniqueConstraint('region_id', 'item_id'),)

    id        = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.BigInteger, db.ForeignKey('universe_regions.id'), nullable=False)
    item_id   = db.Column(db.BigInteger, db.ForeignKey('universe_types.id'), nullable=False)

    universe_region = db.relationship('UniverseRegion')
    universe_type   = db.relationship('UniverseType')
