from evebs.extensions import db


class UniverseCategory(db.Model):
    __tablename__ = 'universe_categories'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)  # called category_id in the fetch request
    name = db.Column(db.Text, nullable=False)
    published = db.Column(db.Boolean, nullable=False)

    universe_groups = db.relationship('UniverseGroup', back_populates='universe_category')
