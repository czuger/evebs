from evebs.extensions import db


class JitaPriceForecastLinearRegression(db.Model):
    """Read-only Postgres materialized view `jita_price_forecast_linear_regression`.

    One row per (type_id, forecast_date) for the next 3 days. Two linear regressions are run
    per item over the volume-weighted daily price (`SUM(volume*price)/SUM(volume)`) of Jita
    `sales_finals`: a **7-day** training window and a **30-day** training window. Each window
    yields a daily forecast (`forecast_7d` / `forecast_30d`), slope/intercept/r²/n and a
    `confidence_7d`/`confidence_30d` ('high'/'medium'/'low'). `spread` / `spread_percent`
    compare the two windows' forecasts per date (absolute, percent relative to the 30-day
    forecast). Refreshed (non-concurrently) by `process/update_price_forecasts.py`.
    """
    __tablename__ = 'jita_price_forecast_linear_regression'
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
