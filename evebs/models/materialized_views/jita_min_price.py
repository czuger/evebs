from evebs.extensions import db


class JitaMinPrice(db.Model):
    """Read-only Postgres materialized view `jita_min_prices`.

    One row per item type with the P10 Jita (system 30000142) sell price computed over
    `public_trade_orders`. Refreshed by `process/update_jita_min_prices.py`
    (`REFRESH MATERIALIZED VIEW CONCURRENTLY`). `is_view` keeps it out of test truncation.
    """
    __tablename__ = 'jita_min_prices'
    __table_args__ = {'info': {'is_view': True}}

    id = db.Column(db.BigInteger, primary_key=True)   # EVE item type_id
    min_sell_price = db.Column(db.Float)
    updated_at = db.Column(db.DateTime)
