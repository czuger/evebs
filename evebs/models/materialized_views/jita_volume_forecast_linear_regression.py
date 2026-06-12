from evebs.extensions import db


class JitaVolumeForecastLinearRegression(db.Model):
    """Read-only Postgres materialized view `jita_volume_forecast_linear_regression`.

    Like `jita_price_forecast_linear_regression` but forecasts daily traded **volume**
    (`SUM(volume)` per day) from Jita `sales_finals`; no price. Two training windows per item
    (7-day and 30-day), each yielding a daily forecast for the next 3 days plus
    slope/intercept/r²/n and a confidence. `spread`/`spread_percent` compare the two windows.
    Refreshed (non-concurrently) by `process/update_price_forecasts.py`.
    """
    __tablename__ = 'jita_volume_forecast_linear_regression'
    __table_args__ = {'info': {'is_view': True}}

    type_id        = db.Column(db.BigInteger, primary_key=True)   # EVE item type_id
    forecast_date  = db.Column(db.Date, primary_key=True)
    forecast_7d    = db.Column(db.Float)    # forecast from the 7-day training window
    forecast_30d   = db.Column(db.Float)    # forecast from the 30-day training window
    spread         = db.Column(db.Float)    # |forecast_30d - forecast_7d|
    spread_percent = db.Column(db.Float)    # |spread / forecast_30d|
    slope_7d       = db.Column(db.Float)
    intercept_7d   = db.Column(db.Float)
    r2_7d          = db.Column(db.Float)
    n_7d           = db.Column(db.BigInteger)
    confidence_7d  = db.Column(db.String)
    slope_30d      = db.Column(db.Float)
    intercept_30d  = db.Column(db.Float)
    r2_30d         = db.Column(db.Float)
    n_30d          = db.Column(db.BigInteger)
    confidence_30d = db.Column(db.String)
