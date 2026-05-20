from sqlalchemy import text
from evebs.extensions import db


def refresh_market_prices():
    """Refresh both market price materialized views concurrently."""
    db.session.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY market_seller_prices"))
    db.session.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY market_buyer_prices"))
    db.session.commit()
