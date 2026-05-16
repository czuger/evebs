import json
from datetime import datetime
from evebs.extensions import db
from evebs.models.associations import eve_items_users


class EveItem(db.Model):
    __tablename__ = 'eve_items'

    id = db.Column(db.Integer, primary_key=True)
    cpp_eve_item_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    cost = db.Column(db.Float)
    market_group_id = db.Column(db.BigInteger, db.ForeignKey('market_groups.id'))
    blueprint_id = db.Column(db.BigInteger, db.ForeignKey('blueprints.id'))
    volume = db.Column(db.Float)
    production_level = db.Column(db.Integer)
    base_item = db.Column(db.Boolean, default=False, nullable=False)
    cpp_market_adjusted_price = db.Column(db.Float)
    cpp_market_average_price = db.Column(db.Float)
    description = db.Column(db.Text)
    _market_group_path = db.Column('market_group_path', db.Text, default='[]', nullable=False)
    mass = db.Column(db.Float)
    packaged_volume = db.Column(db.Float)
    weekly_avg_price = db.Column(db.Float)
    faction = db.Column(db.Boolean, default=False, nullable=False)
    slug = db.Column(db.String, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = db.relationship('User', secondary=eve_items_users, back_populates='eve_items')
    market_group = db.relationship('MarketGroup', back_populates='eve_items')
    blueprint = db.relationship('Blueprint', back_populates='eve_item')
    blueprint_materials = db.relationship('BlueprintMaterial', foreign_keys='BlueprintMaterial.eve_item_id', back_populates='eve_item')
    prices_mins = db.relationship('PricesMin', back_populates='eve_item', cascade='all, delete-orphan')
    sales_finals = db.relationship('SalesFinal', back_populates='eve_item', cascade='all, delete-orphan')
    prices_advices = db.relationship('PricesAdvice', back_populates='eve_item', cascade='all, delete-orphan')
    buy_orders_analytics = db.relationship('BuyOrdersAnalytic', back_populates='eve_item', cascade='all, delete-orphan')
    public_trade_orders = db.relationship('PublicTradeOrder', back_populates='eve_item', cascade='all, delete-orphan')
    eve_market_histories_groups = db.relationship('EveMarketHistoriesGroup', back_populates='eve_item', cascade='all, delete-orphan')
    weekly_price_details = db.relationship('WeeklyPriceDetail', back_populates='eve_item', cascade='all, delete-orphan')

    @property
    def market_group_path(self):
        return json.loads(self._market_group_path or '[]')

    @market_group_path.setter
    def market_group_path(self, value):
        self._market_group_path = json.dumps(value)

    @classmethod
    def find_by_slug(cls, slug):
        item = cls.query.filter_by(slug=slug).first()
        if item is None:
            try:
                item = cls.query.get(int(slug))
            except (ValueError, TypeError):
                pass
        return item

    @classmethod
    def to_eve_item_id(cls, cpp_eve_item_id):
        item = cls.query.filter_by(cpp_eve_item_id=cpp_eve_item_id).first()
        return item.id if item else None
