from evebs.extensions import db


class MarketGroup(db.Model):
    """Eve market category tree node; items sit at leaf groups."""

    __tablename__ = 'market_groups'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)  # called market_group_id in the fetch request
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    parent_group_id = db.Column(db.BigInteger, db.ForeignKey('market_groups.id'))

    parent = db.relationship('MarketGroup', remote_side=[id], backref='children')

    @classmethod
    def roots(cls):
        """Return all top-level groups (no parent)."""
        return cls.query.filter_by(parent_group_id=None)

    def is_leaf(self):
        """True when this group has no children and directly contains items."""
        return not self.children

    def ancestors(self):
        """Return the path from root to this node's parent, root first."""
        chain = []
        node = self.parent
        while node:
            chain.append(node)
            node = node.parent
        chain.reverse()
        return chain
    universe_types = db.relationship('UniverseType', back_populates='market_group')
