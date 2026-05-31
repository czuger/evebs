from evebs.extensions import db


class BuyOrdersAnalyticsResult(db.Model):
    __tablename__ = 'buy_orders_analytics_results'
    __table_args__ = {'info': {'is_view': True}}

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger)
    universe_system_id = db.Column(db.BigInteger)
    eve_item_id = db.Column(db.BigInteger)
    trade_hub_name = db.Column(db.String)
    eve_item_name = db.Column(db.String)
    over_approx_max_price_volume = db.Column(db.BigInteger)
    approx_max_price = db.Column(db.Float)
    single_unit_cost = db.Column(db.Float)
    single_unit_margin = db.Column(db.Float)
    margin_pcent = db.Column(db.Float)
    full_margin = db.Column(db.Float)
    batch_cap = db.Column(db.Float)
    capped_volume = db.Column(db.Float)
    capped_margin = db.Column(db.Float)
