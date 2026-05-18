from evebs.extensions import db


class UniverseGroup(db.Model):
    """Item group under a universe category, one level above UniverseType."""

    __tablename__ = 'universe_groups'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)  # called group_id in the fetch request
    name = db.Column(db.Text, nullable=False)
    published = db.Column(db.Boolean, nullable=False)
    category_id = db.Column(db.BigInteger, db.ForeignKey('universe_categories.id'), nullable=False)

    universe_category = db.relationship('UniverseCategory', back_populates='universe_groups')
    universe_types = db.relationship('UniverseType', back_populates='universe_group')
