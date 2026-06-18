from datetime import UTC, datetime

from evebs.extensions import db


class MarketProphetForecast(db.Model):
    """Prophet 5-day forecast for a (region, type, confidence): predicted daily average,
    lowest and highest price and volume, each with a lower/upper band, plus price/volume
    spread metrics. Every column is populated — a forecast that would produce a null is
    recorded in MarketProphetForecastErrors instead. One row per
    (region_id, type_id, confidence, forecast_date)."""
    __tablename__ = 'market_prophet_forecasts'
    __table_args__ = (
        db.UniqueConstraint('region_id', 'type_id', 'forecast_date',
                            name='uq_market_prophet_forecasts_region_type_date'),
    )

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    region_id = db.Column(db.Integer, nullable=False)
    type_id = db.Column(db.BigInteger, nullable=False)
    forecast_date = db.Column(db.Date, nullable=False)
    generated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    confidence = db.Column(db.Float, nullable=False)

    avg_predicted = db.Column(db.Float, nullable=False)
    avg_lower = db.Column(db.Float, nullable=False)
    avg_upper = db.Column(db.Float, nullable=False)

    low_predicted = db.Column(db.Float, nullable=False)
    low_lower = db.Column(db.Float, nullable=False)
    low_upper = db.Column(db.Float, nullable=False)

    high_predicted = db.Column(db.Float, nullable=False)
    high_lower = db.Column(db.Float, nullable=False)
    high_upper = db.Column(db.Float, nullable=False)

    vol_predicted = db.Column(db.Float, nullable=False)
    vol_lower = db.Column(db.Float, nullable=False)
    vol_upper = db.Column(db.Float, nullable=False)

    price_spread = db.Column(db.Float, nullable=False)       # high_predicted - low_predicted
    price_spread_pct = db.Column(db.Float, nullable=False)   # price_spread / avg_predicted

    # Predicted average-price trend vs the last recorded market price, encoded as:
    #   flat = 0, up = 1, slow_up = 2, down = -1, slow_down = -2, NULL = unknown.
    price_direction = db.Column(db.SmallInteger, nullable=True)
