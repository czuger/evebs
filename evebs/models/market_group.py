from evebs.extensions import db


class MarketGroup(db.Model):
    __tablename__ = 'market_groups'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)  # called market_group_id in the fetch request
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    parent_group_id = db.Column(db.BigInteger, db.ForeignKey('market_groups.id'))

    parent = db.relationship('MarketGroup', remote_side=[id], backref='children')
    universe_types = db.relationship('UniverseType', back_populates='market_group')
    eve_items = db.relationship('EveItem', back_populates='market_group')
