from evebs.extensions import db


class JitaManufacturingMargins(db.Model):
    __tablename__ = 'jita_manufacturing_margins'
    __table_args__ = {'info': {'is_view': True}}

    cpp_eve_item_id         = db.Column(db.Integer, primary_key=True)
    eve_item_id             = db.Column(db.Integer, db.ForeignKey('eve_items.id'))
    manufacturing_cost      = db.Column(db.Float)
    manufacturing_tax       = db.Column(db.Float)
    estimated_selling_price = db.Column(db.Float)
    selling_tax             = db.Column(db.Float)
    benefit                 = db.Column(db.Float)

    eve_item = db.relationship('EveItem', foreign_keys=[eve_item_id])
