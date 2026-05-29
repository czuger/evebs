from evebs.extensions import db


class ComponentToBuy(db.Model):
    __tablename__ = 'components_to_buys'
    __table_args__ = {'info': {'is_view': True}}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    eve_item_name = db.Column(db.String)
    eve_item_id = db.Column(db.Integer)
    qtt_to_buy = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    required_volume = db.Column(db.Float)
    base_item = db.Column(db.Boolean)
