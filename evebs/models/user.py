from datetime import datetime
from flask_login import UserMixin
from evebs.extensions import db, login_manager
from evebs.models.associations import eve_items_users, universe_systems_users


class User(UserMixin, db.Model):
    """Eve character logged in via SSO, with personal watchlist and settings."""

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
    user_location_station_id = db.Column(db.BigInteger, db.ForeignKey('universe_stations.id'))
    avoid_low_sec = db.Column(db.Boolean, default=False, nullable=False)
    avoid_null_sec = db.Column(db.Boolean, default=False, nullable=False)
    max_jumps = db.Column(db.Integer, default=5, nullable=False)
    last_duplication_receiver_id = db.Column(db.Integer)
    facility_tax = db.Column(db.Float, default=0.25, nullable=False)
    scc_surcharge = db.Column(db.Float, default=4.0, nullable=False)
    sales_orders_show_margin_min = db.Column(db.Integer)
    initialization_finalized = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eve_items = db.relationship(
        'UniverseType',
        secondary=eve_items_users,
        primaryjoin='User.id == foreign(eve_items_users.c.user_id)',
        secondaryjoin='foreign(eve_items_users.c.eve_item_id) == UniverseType.id',
        viewonly=True,
    )
    universe_systems = db.relationship(
        'UniverseSystem',
        secondary=universe_systems_users,
        primaryjoin='User.id == foreign(universe_systems_users.c.user_id)',
        secondaryjoin='foreign(universe_systems_users.c.universe_system_id) == UniverseSystem.id',
    )
    production_lists = db.relationship('ProductionList', back_populates='user', cascade='all, delete-orphan')
    blueprint_modifications = db.relationship('BlueprintModification', back_populates='user', cascade='all, delete-orphan')
    user_sale_orders = db.relationship('UserSaleOrder', back_populates='user', cascade='all, delete-orphan')
    user_location_station = db.relationship(
        'UniverseStation', foreign_keys=[user_location_station_id]
    )
    bpc_assets = db.relationship('BpcAsset', back_populates='user', cascade='all, delete-orphan')
    bpc_assets_stations = db.relationship('BpcAssetsStation', back_populates='user', cascade='all, delete-orphan')
    eve_items_saved_lists = db.relationship('EveItemsSavedList', back_populates='user', cascade='all, delete-orphan')

    @property
    def eve_item_ids(self):
        """IDs of all items the user is currently tracking."""
        return [item.id for item in self.eve_items]

    @property
    def trade_hub_ids(self):
        """IDs of all systems the user is monitoring."""
        return [s.id for s in self.universe_systems]


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login callback to reload a user from the session."""
    return db.session.get(User, int(user_id))
