from datetime import datetime

from evebs.extensions import db


class JitaMarketAnalytics(db.Model):
    """Regular table: jita_market_analytics.

    Combines a live Jita price benchmark with a volume-weighted 3-day price forecast
    derived from historical sales data.  One row per EVE item type_id.

    HOW IT IS COMPUTED
    ------------------
    Updated by process/update_jita_market_analytics.py (run after each orders cycle):

      min_sell_price:
        Same P10 algorithm as the jita_prices materialized view — minimum ask price
        after skipping the bottom 10% of cumulative sell-order volume at Jita.
        Source: public_trade_orders (live market orders).

      price_forecast_3d:
        Volume-weighted linear regression over the last 30 days of daily VWAPs
        from sales_finals at Jita (system 30000142).  The fitted line is evaluated
        at CURRENT_DATE + 3 to produce a 3-day ahead price estimate.
        Returns NULL when there is insufficient data or zero variance in dates.

    WHEN IT IS REFRESHED
    --------------------
    Standalone script: process/update_jita_market_analytics.py
      python process/update_jita_market_analytics.py      # update
      python process/update_jita_market_analytics.py -n   # dry-run: print row count
    """

    __tablename__ = 'jita_market_analytics'

    id                = db.Column(db.BigInteger, primary_key=True)  # EVE item type_id
    min_sell_price    = db.Column(db.Float)    # P10 ask price at Jita (live orders)
    price_forecast_3d = db.Column(db.Float)    # volume-weighted 3-day price forecast
    updated_at        = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
