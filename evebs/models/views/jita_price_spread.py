from evebs.extensions import db


class JitaPriceSpread(db.Model):
    """Read-only SQL view: jita_price_spreads.

    Joins jita_min_prices (current P10 Jita ask) with jita_price_forecasts (3-day forecast)
    and eve_items. `spread_pcent` is a fraction ((forecast - current) / current). `direction`
    is 'up'/'down'/'flat' (±2% band) and `is_hard` flags |spread| >= 10%. Forecasts produced
    by the 'min_price' fallback are treated as 'flat' (no real trend).
    """
    __tablename__ = 'jita_price_spreads'
    __table_args__ = {'info': {'is_view': True}}

    id                = db.Column(db.BigInteger, primary_key=True)   # EVE item type_id
    item_name         = db.Column(db.String)
    item_slug         = db.Column(db.String)
    min_sell_price    = db.Column(db.Float)
    price_forecast_3d = db.Column(db.Float)
    method            = db.Column(db.String)
    spread            = db.Column(db.Float)
    spread_pcent      = db.Column(db.Float)
    direction         = db.Column(db.String)
    is_hard           = db.Column(db.Boolean)
