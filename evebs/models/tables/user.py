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
    buy_order_filtering = db.Column(db.JSON, nullable=False, default=lambda: {
        'batch_cap': True,
        'batch_cap_max_runs': 10,
        'min_margin_percent': 20,
        'min_batch_margin_amount': 5_000_000,
    })
    sell_orders_filtering = db.Column(db.JSON, nullable=False, default=lambda: {
        'min_margin_percent': 20,
        'min_batch_margin_amount': 5_000_000,
    })
    remove_occuped_places = db.Column(db.Boolean)
    watch_my_prices = db.Column(db.Boolean)
    last_changes_in_choices = db.Column(db.DateTime)
    download_assets_running = db.Column(db.Boolean, default=False, nullable=False)
    last_assets_download = db.Column(db.DateTime)
    download_orders_running = db.Column(db.Boolean, default=False, nullable=False)
    last_orders_download = db.Column(db.DateTime)
    download_blueprints_running = db.Column(db.Boolean, default=False, nullable=False)
    last_blueprints_download = db.Column(db.DateTime)
    download_industry_jobs_running = db.Column(db.Boolean, default=False, nullable=False)
    last_industry_jobs_download = db.Column(db.DateTime)
    selected_assets_station_id = db.Column(db.BigInteger, db.ForeignKey('universe_stations.id'))
    current_location_station_id = db.Column(db.BigInteger, db.ForeignKey('universe_stations.id'), nullable=True)
    last_duplication_receiver_id = db.Column(db.Integer)
    sales_orders_show_margin_min = db.Column(db.Integer)
    initialization_finalized = db.Column(db.Boolean, default=False, nullable=False)

    # Per-user EVE industry tax configuration.
    #
    # Structure: one key per activity type → dict of cost components (plain %, e.g. 5.0 = 5 %).
    # Divide by 100 before applying to ISK amounts.
    #
    # Keys per activity:
    #   system_cost_index — CCP-set per-system rate (varies with industrial activity level).
    #   scc_tax           — Secure Commerce Commission flat surcharge (CCP-set).
    #   <activity>_tax    — structure owner's tax for that specific job type.
    #
    # Activity-specific third key:
    #   manufacturing  → standard_tax (normal jobs), capital_tax (capital ship jobs)
    #   copying        → copying_tax
    #   invention      → invention_tax
    #   material_research → material_tax
    #   time_research     → time_tax
    #
    # Edited via /users/edit and saved by _parse_taxes() in routes/users.py.
    # Default values represent a quiet high-sec NPC station (5 % SCI, 4 % SCC, 1 % activity).
    # Reaction settings live in their own `reaction_modifications` column (below).
    industry_taxes = db.Column(db.JSON, nullable=False, default=lambda: {
        'manufacturing':     {'system_cost_index': 5.0, 'scc_tax': 4.0, 'standard_tax': 1.0, 'capital_tax': 1.0},
        'material_research': {'system_cost_index': 5.0, 'scc_tax': 4.0, 'material_tax': 1.0},
        'time_research':     {'system_cost_index': 5.0, 'scc_tax': 4.0, 'time_tax': 1.0},
        'copying':           {'system_cost_index': 5.0, 'scc_tax': 4.0, 'copying_tax': 1.0},
        'invention':         {'system_cost_index': 5.0, 'scc_tax': 4.0, 'invention_tax': 1.0},
    })

    # Per-user reaction configuration (plain %, e.g. 5.0 = 5 %), edited on
    # /users/reaction_modifications. system_cost_index + scc_tax + reaction_tax form the
    # reaction job tax; material_consumption is a material-usage modifier that is always
    # <= 0 (a reduction — positive values are clamped to 0) and is applied when computing
    # components to buy for reactions.
    reaction_modifications = db.Column(db.JSON, nullable=False, default=lambda: {
        'system_cost_index': 5.0, 'scc_tax': 4.0, 'reaction_tax': 1.0, 'material_consumption': 0,
    })

    # Per-user sell-order fee configuration (plain %, e.g. 2 = 2 %).
    # broker_fee_taxes: exchange/structure broker fee charged on listing
    # sales_taxes:      CCP transaction tax charged on sale
    # safety_tax:       user-defined undercut/buffer margin
    sales_taxes = db.Column(db.JSON, nullable=False, default=lambda: {
        'broker_fee_taxes': 2,
        'sales_taxes':      4,
        'safety_tax':       0,
    })
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    eve_items = db.relationship('EveItem', secondary=eve_items_users, back_populates='users')
    trade_hubs = db.relationship('UniverseSystem', secondary=trade_hubs_users, back_populates='users')
    blueprints = db.relationship('Blueprint', secondary=user_blueprints, back_populates='users')
    production_lists = db.relationship('ProductionList', back_populates='user', cascade='all, delete-orphan')
    reaction_lists = db.relationship('ReactionList', back_populates='user', cascade='all, delete-orphan')
    invention_lists = db.relationship('InventionList', back_populates='user', cascade='all, delete-orphan')
    copy_lists = db.relationship('CopyList', back_populates='user', cascade='all, delete-orphan')
    industry_jobs = db.relationship('IndustryJob', back_populates='user', cascade='all, delete-orphan')
    blueprint_modifications = db.relationship('BlueprintModification', back_populates='user', cascade='all, delete-orphan')
    user_sale_orders = db.relationship('UserSaleOrder', back_populates='user', cascade='all, delete-orphan')
    user_assets = db.relationship('UserAsset', back_populates='user', cascade='all, delete-orphan')
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
