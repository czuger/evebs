from evebs.extensions import db


class UserSaleOrderDetail(db.Model):
    """Read-only SQL view: user_sale_order_details.

    Enriches the user's active sell orders with market context: current minimum
    market price, manufacturing cost, and the gap between the user's listed price
    and the market price.  Useful for detecting undercuts quickly.

    HOW IT IS COMPUTED
    ------------------
    Source tables:
      - user_sale_orders      – the user's open sell orders (synced via ESI),
                                refreshed by esi/download_my_orders.py when the user
                                clicks "Sync orders" (GET /user_sales_orders/sync)
      - eve_items             – item name
      - blueprints            – manufacturing_cost, prod_qtt
      - universe_*            – for human-readable trade hub name
      - jita_market_analytics – Jita min_sell_price (LEFT JOIN — nullable),
                                updated by process/update_jita_market_analytics.py

    Key derived columns:
      cost                   = blueprints.manufacturing_cost / prod_qtt
      min_price_margin_pcent = jma.min_sell_price / cost - 1.0
      price_delta            = jma.min_sell_price - user_sale_orders.price
        → positive  → user is being undercut (cheaper Jita offer exists)
        → negative  → user has the lowest Jita price
        → NULL      → no Jita analytics data for this item

    WHEN DATA CHANGES
    -----------------
    user_sale_orders is refreshed on demand (user-triggered ESI sync).
    prices_mins is updated every ~15 minutes automatically.
    Being a plain SQL VIEW, results reflect the latest state of both tables
    with no explicit refresh command.

    WHERE IT IS USED
    ----------------
    - evebs/routes/user_sales_orders.py  →  GET /user_sales_orders
        Filters: user_id = current_user.id
        Sorted by price_delta descending (largest undercuts first), so the user
        sees the orders most urgently needing repricing at the top.
    """

    __tablename__ = 'user_sale_order_details'
    __table_args__ = {'info': {'is_view': True}}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    trade_hub_name = db.Column(db.String)           # "SystemName (RegionName)"
    eve_item_name = db.Column(db.String)
    my_price = db.Column(db.Float)                  # user's listed sell price
    min_price = db.Column(db.Float)                 # current market min sell price (nullable)
    cost = db.Column(db.Float)                      # manufacturing cost per unit
    prod_qtt = db.Column(db.Integer)               # blueprint production quantity
    min_price_margin_pcent = db.Column(db.Float)    # market margin: min_price/cost - 1.0
    price_delta = db.Column(db.Float)               # min_price - my_price (+ = undercut)
    eve_item_id = db.Column(db.Integer)
    trade_hub_id = db.Column(db.Integer)
    eve_system_id = db.Column(db.Integer)
