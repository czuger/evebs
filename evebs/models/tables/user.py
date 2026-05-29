from datetime import datetime

from flask_login import UserMixin

from evebs.extensions import db, login_manager
from evebs.models.tables.associations import eve_items_users, trade_hubs_users, user_blueprints


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    provider = db.Column(db.String)
    uid = db.Column(db.String)
    expires_on = db.Column(db.DateTime)
    token = db.Column(db.String)
    renew_token = db.Column(db.String)
    admin = db.Column(db.Boolean, default=False, nullable=False)
    locked = db.Column(db.Boolean, default=False, nullable=False)
    batch_cap = db.Column(db.Boolean, default=True, nullable=False)
    batch_cap_multiplier = db.Column(db.Integer, default=10, nullable=False)
    vol_month_pcent = db.Column(db.Integer, default=5, nullable=False)
    min_pcent_for_advice = db.Column(db.Integer, default=20, nullable=False)
    min_amount_for_advice = db.Column(db.Integer, default=5000000, nullable=False)
    remove_occuped_places = db.Column(db.Boolean)
    watch_my_prices = db.Column(db.Boolean)
    last_changes_in_choices = db.Column(db.DateTime)
    download_assets_running = db.Column(db.Boolean, default=False, nullable=False)
    last_assets_download = db.Column(db.DateTime)
    download_orders_running = db.Column(db.Boolean, default=False, nullable=False)
    last_orders_download = db.Column(db.DateTime)
    download_blueprints_running = db.Column(db.Boolean, default=False, nullable=False)
    last_blueprints_download = db.Column(db.DateTime)
    selected_assets_station_id = db.Column(db.BigInteger, db.ForeignKey('universe_stations.id'))
    last_duplication_receiver_id = db.Column(db.Integer)
    sales_orders_show_margin_min = db.Column(db.Integer)
    initialization_finalized = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eve_items = db.relationship('EveItem', secondary=eve_items_users, back_populates='users')
    trade_hubs = db.relationship('TradeHub', secondary=trade_hubs_users, back_populates='users')
    blueprints = db.relationship('Blueprint', secondary=user_blueprints, back_populates='users')
    production_lists = db.relationship('ProductionList', back_populates='user', cascade='all, delete-orphan')
    blueprint_modifications = db.relationship('BlueprintModification', back_populates='user', cascade='all, delete-orphan')
    user_sale_orders = db.relationship('UserSaleOrder', back_populates='user', cascade='all, delete-orphan')
    bpc_assets = db.relationship('BpcAsset', back_populates='user', cascade='all, delete-orphan')
    bpc_assets_stations = db.relationship('BpcAssetsStation', back_populates='user', cascade='all, delete-orphan')
    eve_items_saved_lists = db.relationship('EveItemsSavedList', back_populates='user', cascade='all, delete-orphan')

    @property
    def eve_item_ids(self):
        return [item.id for item in self.eve_items]

    @property
    def trade_hub_ids(self):
        return [th.id for th in self.trade_hubs]


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
