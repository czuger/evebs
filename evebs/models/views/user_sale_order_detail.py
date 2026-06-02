from evebs.extensions import db


class UserSaleOrderDetail(db.Model):
    __tablename__ = 'user_sale_order_details'
    __table_args__ = {'info': {'is_view': True}}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    trade_hub_name = db.Column(db.String)
    eve_item_name = db.Column(db.String)
    my_price = db.Column(db.Float)
    min_price = db.Column(db.Float)
    cost = db.Column(db.Float)
    prod_qtt = db.Column(db.Integer)
    min_price_margin_pcent = db.Column(db.Float)
    price_delta = db.Column(db.Float)
    eve_item_id = db.Column(db.Integer)
    trade_hub_id = db.Column(db.Integer)
    eve_system_id = db.Column(db.Integer)
