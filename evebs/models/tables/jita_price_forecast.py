from datetime import datetime

from evebs.extensions import db


class JitaPriceForecast(db.Model):
    """3-day Jita price forecast per item type.

    Recomputed by process/update_price_forecasts.py from market_histories (The Forge,
    region 10000002), with jita_min_prices as the <14-day fallback. `method` records the
    tier that produced the value ('linear' | 'min_price'; later 'prophet' for the >=90-day
    tier).
    """
    __tablename__ = 'jita_price_forecasts'

    id                = db.Column(db.BigInteger, primary_key=True)   # EVE item type_id
    price_forecast_3d = db.Column(db.Float)
    method            = db.Column(db.String, nullable=False)
    updated_at        = db.Column(db.DateTime, default=datetime.utcnow)
