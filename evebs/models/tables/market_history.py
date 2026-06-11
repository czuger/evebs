from datetime import datetime

from evebs.extensions import db


class MarketHistory(db.Model):
    """Verbatim ESI markets/{region}/history daily record for a (region, type).

    Surrogate autoincrement id PK; UNIQUE(region_id, type_id, date) makes inserts
    idempotent. No FKs — type_id is a raw EVE id that need not exist in eve_items
    (mirrors JitaMarketAnalytics).
    """
    __tablename__ = 'market_histories'

    id          = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    region_id   = db.Column(db.Integer, nullable=False)
    type_id     = db.Column(db.BigInteger, nullable=False)
    date        = db.Column(db.Date, nullable=False)
    average     = db.Column(db.Float)
    highest     = db.Column(db.Float)
    lowest      = db.Column(db.Float)
    order_count = db.Column(db.BigInteger)
    volume      = db.Column(db.BigInteger)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('region_id', 'type_id', 'date',
                            name='uq_market_histories_region_type_date'),
    )
