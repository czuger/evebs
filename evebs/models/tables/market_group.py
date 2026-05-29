from datetime import datetime

from evebs.extensions import db


class MarketGroup(db.Model):
    __tablename__ = 'market_groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('market_groups.id'))
    cpp_market_group_id = db.Column(db.Integer, nullable=False, unique=True)
    cpp_parent_market_group_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent = db.relationship('MarketGroup', remote_side=[id], backref='children')
    eve_items = db.relationship('EveItem', back_populates='market_group')

    @classmethod
    def roots(cls):
        return cls.query.filter_by(parent_id=None).order_by(cls.name)

    def is_leaf(self):
        return len(self.children) == 0

    def ancestors(self):
        result = []
        current = self.parent
        while current:
            result.insert(0, current)
            current = current.parent
        return result
