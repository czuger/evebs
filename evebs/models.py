import json
from datetime import datetime, date
from flask_login import UserMixin
from evebs.extensions import db, login_manager


# Association tables
eve_items_users = db.Table('eve_items_users',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('eve_item_id', db.Integer, db.ForeignKey('eve_items.id')),
)

trade_hubs_users = db.Table('trade_hubs_users',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('trade_hub_id', db.Integer, db.ForeignKey('trade_hubs.id')),
)


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


class Region(db.Model):
    __tablename__ = 'regions'

    id = db.Column(db.Integer, primary_key=True)
    cpp_region_id = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trade_hubs = db.relationship('TradeHub', back_populates='region')


class TradeHub(db.Model):
    __tablename__ = 'trade_hubs'

    id = db.Column(db.Integer, primary_key=True)
    eve_system_id = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'))
    inner = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    region = db.relationship('Region', back_populates='trade_hubs')
    users = db.relationship('User', secondary=trade_hubs_users, back_populates='trade_hubs')
    stations = db.relationship('Station', back_populates='trade_hub')
    prices_mins = db.relationship('PricesMin', back_populates='trade_hub')
    prices_advices = db.relationship('PricesAdvice', back_populates='trade_hub')
    public_trade_orders = db.relationship('PublicTradeOrder', back_populates='trade_hub')
    buy_orders_analytics = db.relationship('BuyOrdersAnalytic', back_populates='trade_hub')
    production_lists = db.relationship('ProductionList', back_populates='trade_hub')
    user_sale_orders = db.relationship('UserSaleOrder', back_populates='trade_hub')
    sales_finals = db.relationship('SalesFinal', back_populates='trade_hub')
    weekly_price_details = db.relationship('WeeklyPriceDetail', back_populates='trade_hub')


class MarketGroup(db.Model):
    __tablename__ = 'market_groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('market_groups.id'))
    cpp_market_group_id = db.Column(db.Integer, nullable=False, unique=True)
    cpp_parent_market_group_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent = db.relationship('MarketGroup', remote_side=[id], backref='children')
    eve_items = db.relationship('EveItem', back_populates='market_group')

    @classmethod
    def roots(cls):
        return cls.query.filter_by(parent_id=None).order_by(cls.name)

    def is_leaf(self):
        return len(self.children) == 0

    def ancestors(self):
        result = []
        current = self.parent
        while current:
            result.insert(0, current)
            current = current.parent
        return result


class Blueprint(db.Model):
    __tablename__ = 'blueprints'

    id = db.Column(db.Integer, primary_key=True)
    produced_cpp_type_id = db.Column(db.Integer, nullable=False, unique=True)
    nb_runs = db.Column(db.Integer, nullable=False)
    prod_qtt = db.Column(db.Integer, nullable=False)
    cpp_blueprint_id = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eve_item = db.relationship('EveItem', back_populates='blueprint', uselist=False)
    blueprint_materials = db.relationship('BlueprintMaterial', back_populates='blueprint', cascade='all, delete-orphan')
    blueprint_modifications = db.relationship('BlueprintModification', back_populates='blueprint')

    @property
    def batch_elements_count(self):
        return self.prod_qtt * self.nb_runs


class EveItem(db.Model):
    __tablename__ = 'eve_items'

    id = db.Column(db.Integer, primary_key=True)
    cpp_eve_item_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    cost = db.Column(db.Float)
    market_group_id = db.Column(db.Integer, db.ForeignKey('market_groups.id'))
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
    blueprint_materials = db.relationship('BlueprintMaterial', foreign_keys='BlueprintMaterial.eve_item_id')
    prices_mins = db.relationship('PricesMin', back_populates='eve_item', cascade='all, delete-orphan')
    sales_finals = db.relationship('SalesFinal', back_populates='eve_item', cascade='all, delete-orphan')
    prices_advices = db.relationship('PricesAdvice', back_populates='eve_item', cascade='all, delete-orphan')
    buy_orders_analytics = db.relationship('BuyOrdersAnalytic', back_populates='eve_item', cascade='all, delete-orphan')
    public_trade_orders = db.relationship('PublicTradeOrder', back_populates='eve_item', cascade='all, delete-orphan')
    eve_market_histories_groups = db.relationship('EveMarketHistoriesGroup', back_populates='eve_item', cascade='all, delete-orphan')
    price_advices_min_prices = db.relationship('PriceAdvicesMinPrice', back_populates='eve_item')
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


class BlueprintMaterial(db.Model):
    __tablename__ = 'blueprint_materials'

    id = db.Column(db.Integer, primary_key=True)
    blueprint_id = db.Column(db.Integer, db.ForeignKey('blueprints.id'), nullable=False)
    required_qtt = db.Column(db.Integer, nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    blueprint = db.relationship('Blueprint', back_populates='blueprint_materials')
    eve_item = db.relationship('EveItem', foreign_keys=[eve_item_id])


class BlueprintModification(db.Model):
    __tablename__ = 'blueprint_modifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    blueprint_id = db.Column(db.BigInteger, db.ForeignKey('blueprints.id'), nullable=False)
    percent_modification_value = db.Column(db.Float, nullable=False)
    touched = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='blueprint_modifications')
    blueprint = db.relationship('Blueprint', back_populates='blueprint_modifications')


class PricesMin(db.Model):
    __tablename__ = 'prices_mins'

    id = db.Column(db.Integer, primary_key=True)
    eve_item_id = db.Column(db.Integer, db.ForeignKey('eve_items.id'))
    trade_hub_id = db.Column(db.Integer, db.ForeignKey('trade_hubs.id'))
    min_price = db.Column(db.Float)
    volume = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    eve_item = db.relationship('EveItem', back_populates='prices_mins')
    trade_hub = db.relationship('TradeHub', back_populates='prices_mins')


class PricesAdvice(db.Model):
    __tablename__ = 'prices_advices'

    id = db.Column(db.Integer, primary_key=True)
    eve_item_id = db.Column(db.Integer, db.ForeignKey('eve_items.id'), nullable=False)
    trade_hub_id = db.Column(db.Integer, db.ForeignKey('trade_hubs.id'), nullable=False)
    vol_month = db.Column(db.BigInteger)
    avg_price_month = db.Column(db.Float)
    immediate_montly_pcent = db.Column(db.Float)
    margin_percent = db.Column(db.Float)
    avg_price_week = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eve_item = db.relationship('EveItem', back_populates='prices_advices')
    trade_hub = db.relationship('TradeHub', back_populates='prices_advices')


class PublicTradeOrder(db.Model):
    __tablename__ = 'public_trade_orders'

    id = db.Column(db.BigInteger, primary_key=True)
    trade_hub_id = db.Column(db.BigInteger, db.ForeignKey('trade_hubs.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    order_id = db.Column(db.BigInteger, nullable=False, unique=True)
    is_buy_order = db.Column(db.Boolean, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    range = db.Column(db.String, nullable=False)
    volume_remain = db.Column(db.BigInteger, nullable=False)
    volume_total = db.Column(db.BigInteger, nullable=False)
    min_volume = db.Column(db.BigInteger, nullable=False)
    touched = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trade_hub = db.relationship('TradeHub', back_populates='public_trade_orders')
    eve_item = db.relationship('EveItem', back_populates='public_trade_orders')


class BuyOrdersAnalytic(db.Model):
    __tablename__ = 'buy_orders_analytics'

    id = db.Column(db.BigInteger, primary_key=True)
    trade_hub_id = db.Column(db.BigInteger, db.ForeignKey('trade_hubs.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    approx_max_price = db.Column(db.Float)
    over_approx_max_price_volume = db.Column(db.BigInteger)
    single_unit_cost = db.Column(db.Float)
    single_unit_margin = db.Column(db.Float)
    estimated_volume_margin = db.Column(db.Float)
    per_job_margin = db.Column(db.Float)
    per_job_run_margin = db.Column(db.Float)
    final_margin = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trade_hub = db.relationship('TradeHub', back_populates='buy_orders_analytics')
    eve_item = db.relationship('EveItem', back_populates='buy_orders_analytics')


class SalesFinal(db.Model):
    __tablename__ = 'sales_finals'

    id = db.Column(db.BigInteger, primary_key=True)
    day = db.Column(db.Date, nullable=False)
    trade_hub_id = db.Column(db.BigInteger, db.ForeignKey('trade_hubs.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    volume = db.Column(db.BigInteger, nullable=False)
    price = db.Column(db.Float, nullable=False)
    order_id = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trade_hub = db.relationship('TradeHub', back_populates='sales_finals')
    eve_item = db.relationship('EveItem', back_populates='sales_finals')


class ProductionList(db.Model):
    __tablename__ = 'production_lists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trade_hub_id = db.Column(db.Integer, db.ForeignKey('trade_hubs.id'), nullable=False)
    eve_item_id = db.Column(db.Integer, db.ForeignKey('eve_items.id'), nullable=False)
    runs_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='production_lists')
    trade_hub = db.relationship('TradeHub', back_populates='production_lists')
    eve_item = db.relationship('EveItem')


class UserSaleOrder(db.Model):
    __tablename__ = 'user_sale_orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    eve_item_id = db.Column(db.Integer, db.ForeignKey('eve_items.id'), nullable=False)
    trade_hub_id = db.Column(db.Integer, db.ForeignKey('trade_hubs.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='user_sale_orders')
    eve_item = db.relationship('EveItem')
    trade_hub = db.relationship('TradeHub', back_populates='user_sale_orders')


class EveItemsSavedList(db.Model):
    __tablename__ = 'eve_items_saved_lists'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String, nullable=False)
    saved_ids = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='eve_items_saved_lists')

    def get_ids(self):
        return json.loads(self.saved_ids)

    def set_ids(self, ids):
        self.saved_ids = json.dumps(ids)


class EveMarketHistoriesGroup(db.Model):
    __tablename__ = 'eve_market_histories_groups'

    id = db.Column(db.BigInteger, primary_key=True)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    volume = db.Column(db.BigInteger, nullable=False)
    highest = db.Column(db.Float)
    lowest = db.Column(db.Float)
    average = db.Column(db.Float)
    universe_region_id = db.Column(db.BigInteger, db.ForeignKey('universe_regions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eve_item = db.relationship('EveItem', back_populates='eve_market_histories_groups')
    universe_region = db.relationship('UniverseRegion', back_populates='eve_market_histories_groups')


class UniverseRegion(db.Model):
    __tablename__ = 'universe_regions'

    id = db.Column(db.BigInteger, primary_key=True)
    cpp_region_id = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    orders_pages_count = db.Column(db.Integer, default=0, nullable=False)
    _market_items = db.Column('market_items', db.Text, default='[]', nullable=False)
    market_items_count = db.Column(db.Integer, default=0, nullable=False)
    download_process_id = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eve_market_histories_groups = db.relationship('EveMarketHistoriesGroup', back_populates='universe_region')
    universe_constellations = db.relationship('UniverseConstellation', back_populates='universe_region')

    @property
    def market_items(self):
        return json.loads(self._market_items or '[]')

    @market_items.setter
    def market_items(self, value):
        self._market_items = json.dumps(value)


class UniverseConstellation(db.Model):
    __tablename__ = 'universe_constellations'

    id = db.Column(db.BigInteger, primary_key=True)
    cpp_constellation_id = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    universe_region_id = db.Column(db.BigInteger, db.ForeignKey('universe_regions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    universe_region = db.relationship('UniverseRegion', back_populates='universe_constellations')
    universe_systems = db.relationship('UniverseSystem', back_populates='universe_constellation')


class UniverseSystem(db.Model):
    __tablename__ = 'universe_systems'

    id = db.Column(db.BigInteger, primary_key=True)
    cpp_system_id = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    trade_hub = db.Column(db.Boolean, default=False, nullable=False)
    cpp_star_id = db.Column(db.Integer)
    security_class = db.Column(db.String)
    security_status = db.Column(db.Float, nullable=False)
    kill_stats_current_month = db.Column(db.Integer, default=0, nullable=False)
    kill_stats_last_month = db.Column(db.Integer, default=0, nullable=False)
    universe_constellation_id = db.Column(db.BigInteger, db.ForeignKey('universe_constellations.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    universe_constellation = db.relationship('UniverseConstellation', back_populates='universe_systems')
    structures = db.relationship('Structure', back_populates='universe_system')
    universe_stations = db.relationship('UniverseStation', back_populates='universe_system')


class UniverseStation(db.Model):
    __tablename__ = 'universe_stations'

    id = db.Column(db.BigInteger, primary_key=True)
    cpp_station_id = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    _services = db.Column('services', db.Text, nullable=False, default='[]')
    office_rental_cost = db.Column(db.Float, nullable=False)
    security_status = db.Column(db.Float)
    jita_distance = db.Column(db.Integer)
    _industry_costs_indices = db.Column('industry_costs_indices', db.Text)
    universe_system_id = db.Column(db.BigInteger, db.ForeignKey('universe_systems.id'), nullable=False)
    station_id = db.Column(db.BigInteger, db.ForeignKey('stations.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    universe_system = db.relationship('UniverseSystem', back_populates='universe_stations')

    @property
    def services(self):
        return json.loads(self._services or '[]')

    @services.setter
    def services(self, value):
        self._services = json.dumps(value)

    @property
    def industry_costs_indices(self):
        return json.loads(self._industry_costs_indices or '{}') if self._industry_costs_indices else {}

    @industry_costs_indices.setter
    def industry_costs_indices(self, value):
        self._industry_costs_indices = json.dumps(value) if value else None


class Station(db.Model):
    __tablename__ = 'stations'

    id = db.Column(db.Integer, primary_key=True)
    trade_hub_id = db.Column(db.Integer, db.ForeignKey('trade_hubs.id'))
    name = db.Column(db.String)
    cpp_station_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    trade_hub = db.relationship('TradeHub', back_populates='stations')

    @classmethod
    def to_trade_hub_id(cls, location_id):
        station = cls.query.filter_by(cpp_station_id=location_id).first()
        return station.trade_hub_id if station else None


class Structure(db.Model):
    __tablename__ = 'structures'

    id = db.Column(db.BigInteger, primary_key=True)
    cpp_structure_id = db.Column(db.BigInteger, nullable=False, unique=True)
    forbidden = db.Column(db.Boolean, default=True, nullable=False)
    universe_system_id = db.Column(db.BigInteger, db.ForeignKey('universe_systems.id'))
    orders_count_pages = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    universe_system = db.relationship('UniverseSystem', back_populates='structures')


class Constant(db.Model):
    __tablename__ = 'constants'

    id = db.Column(db.BigInteger, primary_key=True)
    libe = db.Column(db.String, nullable=False, unique=True)
    f_value = db.Column(db.Float)
    description = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LastUpdate(db.Model):
    __tablename__ = 'last_updates'

    id = db.Column(db.BigInteger, primary_key=True)
    update_type = db.Column(db.String, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    def set(cls, update_type):
        record = cls.query.filter_by(update_type=str(update_type)).first()
        if record:
            record.updated_at = datetime.utcnow()
        else:
            record = cls(update_type=str(update_type), updated_at=datetime.utcnow())
            db.session.add(record)
        db.session.commit()


class Crontab(db.Model):
    __tablename__ = 'crontabs'

    id = db.Column(db.BigInteger, primary_key=True)
    cron_name = db.Column(db.String, nullable=False)
    status = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def start(cls, cron_name):
        import os
        if os.environ.get('FLASK_ENV') == 'development':
            return
        record = cls.query.filter_by(cron_name=str(cron_name)).first()
        if not record:
            record = cls(cron_name=str(cron_name), status=False)
            db.session.add(record)
        if record.status:
            print('Process actually running. Exiting')
            import sys
            sys.exit(0)
        record.status = True
        record.updated_at = datetime.utcnow()
        db.session.commit()

    @classmethod
    def stop(cls, cron_name):
        cls.query.filter_by(cron_name=str(cron_name)).update(
            {'status': False, 'updated_at': datetime.utcnow()}
        )
        db.session.commit()


class WeeklyPriceDetail(db.Model):
    __tablename__ = 'weekly_price_details'

    id = db.Column(db.BigInteger, primary_key=True)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    trade_hub_id = db.Column(db.BigInteger, db.ForeignKey('trade_hubs.id'), nullable=False)
    day = db.Column(db.Date, nullable=False)
    volume = db.Column(db.Float, nullable=False)
    weighted_avg_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eve_item = db.relationship('EveItem', back_populates='weekly_price_details')
    trade_hub = db.relationship('TradeHub', back_populates='weekly_price_details')


class BpcAsset(db.Model):
    __tablename__ = 'bpc_assets'

    id = db.Column(db.BigInteger, primary_key=True)
    universe_station_id = db.Column(db.BigInteger, db.ForeignKey('universe_stations.id'))
    quantity = db.Column(db.BigInteger, nullable=False)
    touched = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    eve_item_id = db.Column(db.BigInteger, db.ForeignKey('eve_items.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='bpc_assets')


class BpcAssetsStation(db.Model):
    __tablename__ = 'bpc_assets_stations'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    universe_station_id = db.Column(db.BigInteger, db.ForeignKey('universe_stations.id'), nullable=False)
    touched = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='bpc_assets_stations')
    universe_station = db.relationship('UniverseStation')


class UserToUserDuplicationRequest(db.Model):
    __tablename__ = 'user_to_user_duplication_requests'

    id = db.Column(db.BigInteger, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    duplication_type = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])


class UserActivityLog(db.Model):
    __tablename__ = 'user_activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String)
    action = db.Column(db.String)
    user = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# View-backed models (read-only, no migration needed — created by _create_views())
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
