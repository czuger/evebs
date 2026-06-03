from evebs.extensions import db


class BuyOrdersAnalyticsResult(db.Model):
    """Read-only SQL view: buy_orders_analytics_results.

    Joins buy_orders_analytics with user preferences (selected items + trade hubs) to
    produce per-user, per-item, per-hub profitability rows.  Only items that the user
    has added to their watch list AND that are available at one of their trade hubs
    appear here.

    HOW IT IS COMPUTED
    ------------------
    Source tables (all real tables, not views):
      - buy_orders_analytics  – pre-aggregated buy-order stats per item/hub,
                                updated hourly by process/update_prices.py::update_buy_orders_analytics()
      - eve_items, blueprints – static item + blueprint metadata
      - universe_systems / universe_constellations / universe_regions – for human-readable names
      - trade_hubs_users      – which hubs the user selected
      - eve_items_users        – which items the user is watching
      - users                 – user settings (batch_cap_multiplier)

    Key derived columns:
      margin_pcent    = 1 - (cost / approx_max_price)
      full_margin     = over_approx_max_price_volume × single_unit_margin
      batch_cap       = blueprint.nb_runs × blueprint.prod_qtt × user.batch_cap_multiplier
      capped_volume   = MIN(over_approx_max_price_volume, batch_cap)
      capped_margin   = capped_volume × single_unit_margin

    WHEN DATA CHANGES
    -----------------
    Underlying buy_orders_analytics is refreshed every ~15 minutes by
    process/orders_daemon.py (or once per run of process/hourly.py), which calls
    process/update_prices.py::update_buy_orders_analytics().
    Being a plain SQL VIEW (not materialized), results are live the moment the
    underlying tables change — no explicit refresh command is needed.

    WHERE IT IS USED
    ----------------
    - evebs/routes/buy_orders.py  →  GET /buy_orders
      Filters: user_id = current_user.id, capped_margin OR full_margin > 0
      Sorted by margin descending.  Shown as the main "Buy orders" screen.
    """

    __tablename__ = 'buy_orders_analytics_results'
    __table_args__ = {'info': {'is_view': True}}

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger)
    universe_system_id = db.Column(db.BigInteger)
    eve_item_id = db.Column(db.BigInteger)
    trade_hub_name = db.Column(db.String)           # "SystemName (RegionName)"
    eve_item_name = db.Column(db.String)
    over_approx_max_price_volume = db.Column(db.BigInteger)  # volume of buy orders ≥ approx_max_price
    approx_max_price = db.Column(db.Float)          # 90th-percentile buy order price
    single_unit_cost = db.Column(db.Float)          # eve_items.cost (manufacturing cost)
    single_unit_margin = db.Column(db.Float)        # approx_max_price - cost
    margin_pcent = db.Column(db.Float)              # 1 - cost/approx_max_price
    full_margin = db.Column(db.Float)               # volume × single_unit_margin (uncapped)
    batch_cap = db.Column(db.Float)                 # max producible units given user settings
    capped_volume = db.Column(db.Float)             # MIN(volume, batch_cap)
    capped_margin = db.Column(db.Float)             # capped_volume × single_unit_margin
