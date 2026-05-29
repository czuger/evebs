from evebs.extensions import db


class PriceAdvicesMinPrice(db.Model):
    __tablename__ = 'price_advices_min_prices'
    __table_args__ = {'info': {'is_view': True}}

    id = db.Column(db.Integer, primary_key=True)
    eve_item_id = db.Column(db.Integer)
    trade_hub_id = db.Column(db.Integer)
    trade_hub_name = db.Column(db.String)
    item_name = db.Column(db.String)
    cost = db.Column(db.Float)
    min_price = db.Column(db.Float)
    avg_price_week = db.Column(db.Float)
    avg_price_month = db.Column(db.Float)
    vol_month = db.Column(db.BigInteger)
    full_batch_size = db.Column(db.Integer)
    immediate_montly_pcent = db.Column(db.Float)
    margin_percent = db.Column(db.Float)
    avg_monthly_margin_percent = db.Column(db.Float)

    eve_item = db.relationship('EveItem', foreign_keys=[eve_item_id],
                               primaryjoin='PriceAdvicesMinPrice.eve_item_id == EveItem.id',
                               viewonly=True)
