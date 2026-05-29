from evebs.extensions import db


class JitaPrices(db.Model):
    __tablename__ = 'jita_prices'
    __table_args__ = {'info': {'is_view': True}}

    cpp_eve_item_id = db.Column(db.Integer, primary_key=True)
    min_sell_price = db.Column(db.Float)
    max_buy_price = db.Column(db.Float)
    spread = db.Column(db.Float)
