from datetime import UTC, datetime

from evebs.extensions import db


class MarketProphetForecastErrors(db.Model):
    """Records why a (region, type, confidence) could not produce a complete forecast
    (e.g. not_enough_history, unreliable_volume, zero_division). One row per key."""
    __tablename__ = 'market_prophet_forecast_errors'
    __table_args__ = (
        db.UniqueConstraint('region_id', 'type_id', 'confidence',
                            name='uq_market_prophet_forecast_errors_region_type_conf'),
    )

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    region_id = db.Column(db.Integer, nullable=False)
    type_id = db.Column(db.BigInteger, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
