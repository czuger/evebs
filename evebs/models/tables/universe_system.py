from datetime import datetime

from evebs.extensions import db


class UniverseSystem(db.Model):
    __tablename__ = 'universe_systems'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String, nullable=False)
    trade_hub = db.Column(db.Boolean, default=False, nullable=False)
    is_inner = db.Column(db.Boolean, default=False, nullable=False)
    star_id = db.Column(db.Integer)
    security_class = db.Column(db.String)
    security_status = db.Column(db.Float, nullable=False)
    kill_stats_current_month = db.Column(db.Integer, default=0, nullable=False)
    kill_stats_last_month = db.Column(db.Integer, default=0, nullable=False)
    universe_constellation_id = db.Column(db.Integer, db.ForeignKey('universe_constellations.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    universe_constellation = db.relationship('UniverseConstellation', back_populates='universe_systems')
    universe_structures = db.relationship('UniverseStructure', back_populates='universe_system')
    universe_stations = db.relationship('UniverseStation', back_populates='universe_system')
    users = db.relationship('User', secondary='trade_hubs_users', back_populates='trade_hubs')
    public_trade_orders = db.relationship('PublicTradeOrder', back_populates='universe_system')
    production_lists = db.relationship('ProductionList', back_populates='universe_system')
    invention_lists = db.relationship('InventionList', back_populates='universe_system')
    copy_lists = db.relationship('CopyList', back_populates='universe_system')
    user_sale_orders = db.relationship('UserSaleOrder', back_populates='universe_system')
    sales_finals = db.relationship('SalesFinal', back_populates='universe_system')
