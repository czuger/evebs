from evebs.extensions import db


class PriceAdviceMarginComp(db.Model):
    __tablename__ = 'price_advice_margin_comps'
    __table_args__ = {'info': {'is_view': True}}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    item_id = db.Column(db.Integer)
    trade_hub_id = db.Column(db.Integer)
    region_name = db.Column(db.String)
    trade_hub_name = db.Column(db.String)
    item_name = db.Column(db.String)
    single_unit_cost = db.Column(db.Float)
    min_price = db.Column(db.Float)
    price_avg_week = db.Column(db.Float)
    vol_month = db.Column(db.BigInteger)
    full_batch_size = db.Column(db.Integer)
    daily_monthly_pcent = db.Column(db.Float)
    margin_percent = db.Column(db.Float)
    batch_size_formula = db.Column(db.Float)
    min_amount_for_advice = db.Column(db.Integer)
    min_pcent_for_advice = db.Column(db.Integer)
    margin_comp_immediate = db.Column(db.Float)
    margin_comp_weekly = db.Column(db.Float)
