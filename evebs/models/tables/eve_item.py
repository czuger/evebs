import json
from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB

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
    # Per-item Prophet configuration, precomputed by process/compute_prophet_params.py from
    # the item's Forge (region 10000002) price history and read by
    # process/refresh_market_forecast.py to fit Prophet with item-tuned hyper-parameters.
    # GIN-indexed JSONB. Shape:
    #   {
    #     "status": "ok" | "insufficient_data",   # only "ok" items are forecast
    #     "computed_at": "<ISO-8601 UTC>",
    #     "data_summary": {                        # metrics the params are derived from
    #         "data_days": int, "missing_ratio": float, "avg_price": float,
    #         "avg_volume": float, "volatility": float, "trend_strength": float,  # abs R²
    #         "trend_direction": "up"|"down", "price_range_ratio": float,
    #         "outlier_ratio": float, "reliability_score": float  # 0-100 composite
    #     },
    #     "prophet_params": {                      # fed straight into prophet.Prophet(**…)
    #         "changepoint_prior_scale": float, "seasonality_prior_scale": float,
    #         "seasonality_mode": "additive"|"multiplicative", "n_changepoints": int,
    #         "changepoint_range": float, "yearly_seasonality": bool,
    #         "weekly_seasonality": bool, "interval_width": float
    #     },
    #     "runtime_config": {                      # how the forecast script applies the fit
    #         "log_transform": bool, "forecast_days": int
    #     }
    #   }
    # 'insufficient_data' items only carry status/computed_at/data_days (no params).
    prophet_parameters = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = db.relationship('User', secondary=eve_items_users, back_populates='eve_items')
    market_group = db.relationship('MarketGroup', back_populates='eve_items')
    blueprint = db.relationship('Blueprint', back_populates='eve_item')
    sales_finals = db.relationship('SalesFinal', back_populates='eve_item', cascade='all, delete-orphan')
    public_trade_orders = db.relationship('PublicTradeOrder', back_populates='eve_item', cascade='all, delete-orphan')

    @property
    def prophet_ready(self):
        """True when prophet_parameters were computed successfully (status == 'ok')."""
        return (self.prophet_parameters or {}).get('status') == 'ok'

    @property
    def prophet_params(self):
        """The Prophet hyper-parameters dict (empty when not computed)."""
        return (self.prophet_parameters or {}).get('prophet_params', {})

    @property
    def prophet_runtime(self):
        """The runtime_config dict (log_transform / forecast_days)."""
        return (self.prophet_parameters or {}).get('runtime_config', {})

    @property
    def prophet_reliability(self):
        """The 0-100 reliability_score, or None when not computed."""
        return (self.prophet_parameters or {}).get('data_summary', {}).get('reliability_score')

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
