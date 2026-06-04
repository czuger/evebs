import json
from datetime import datetime

from evebs.extensions import db
from evebs.models.tables.associations import eve_items_users


class EveItem(db.Model):
    __tablename__ = 'eve_items'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    name = db.Column(db.String, nullable=False)
    market_group_id = db.Column(db.Integer, db.ForeignKey('market_groups.id'))
    blueprint_id = db.Column(db.Integer, db.ForeignKey('blueprints.id'))
    volume = db.Column(db.Float)
    production_level = db.Column(db.Integer)
    base_item = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.Text)
    _market_group_path = db.Column('market_group_path', db.Text, default='[]', nullable=False)
    mass = db.Column(db.Float)
    packaged_volume = db.Column(db.Float)
    faction = db.Column(db.Boolean, default=False, nullable=False)
    slug = db.Column(db.String, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = db.relationship('User', secondary=eve_items_users, back_populates='eve_items')
    market_group = db.relationship('MarketGroup', back_populates='eve_items')
    blueprint = db.relationship('Blueprint', back_populates='eve_item')
    sales_finals = db.relationship('SalesFinal', back_populates='eve_item', cascade='all, delete-orphan')
    buy_orders_analytics = db.relationship('BuyOrdersAnalytic', back_populates='eve_item', cascade='all, delete-orphan')
    public_trade_orders = db.relationship('PublicTradeOrder', back_populates='eve_item', cascade='all, delete-orphan')
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
    def to_eve_item_id(cls, type_id):
        item = cls.query.get(type_id)
        return item.id if item else None
