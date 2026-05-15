from evebs.extensions import db


class BuyOrdersAnalyticsResult(db.Model):
    __tablename__ = 'buy_orders_analytics_results'
    __table_args__ = {'info': {'is_view': True}}

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger)
    trade_hub_id = db.Column(db.BigInteger)
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
    cpp_eve_item_id = db.Column(db.Integer)
    eve_system_id = db.Column(db.Integer)


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
