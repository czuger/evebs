from evebs.extensions import db
from evebs.models.associations import trade_hubs_users


class TradeHub(db.Model):
    __tablename__ = 'trade_hubs'

    id = db.Column(db.Integer, primary_key=True)
    eve_system_id = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    region_id = db.Column(db.BigInteger, db.ForeignKey('universe_regions.id'))
    inner = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    universe_region = db.relationship('UniverseRegion', back_populates='trade_hubs')
    users = db.relationship('User', secondary=trade_hubs_users, back_populates='trade_hubs')
    prices_mins = db.relationship('PricesMin', back_populates='trade_hub')
    prices_advices = db.relationship('PricesAdvice', back_populates='trade_hub')
    public_trade_orders = db.relationship('PublicTradeOrder', back_populates='trade_hub')
    buy_orders_analytics = db.relationship('BuyOrdersAnalytic', back_populates='trade_hub')
    production_lists = db.relationship('ProductionList', back_populates='trade_hub')
    user_sale_orders = db.relationship('UserSaleOrder', back_populates='trade_hub')
    sales_finals = db.relationship('SalesFinal', back_populates='trade_hub')
    weekly_price_details = db.relationship('WeeklyPriceDetail', back_populates='trade_hub')
