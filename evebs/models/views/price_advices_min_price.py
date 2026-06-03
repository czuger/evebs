from evebs.extensions import db


class PriceAdvicesMinPrice(db.Model):
    """Read-only SQL view: price_advices_min_prices.

    Enriches prices_advices with the current minimum sell price from prices_mins,
    the blueprint batch size, and a derived avg_monthly_margin_percent.  Not filtered
    by user — used by routes that display market-wide data or iterate over all items.

    HOW IT IS COMPUTED
    ------------------
    Source tables:
      - prices_advices  – weekly/monthly price statistics per item/hub,
                          updated by process/update_prices.py::update_prices_advices_immediate()
      - prices_mins     – current minimum sell price per item/hub (LEFT JOIN — nullable),
                          updated by process/update_prices.py::update_prices_min()
      - eve_items       – item metadata including manufacturing cost
      - blueprints      – for full_batch_size = nb_runs × prod_qtt
      - universe_*      – for human-readable trade hub name

    Key derived column:
      avg_monthly_margin_percent = avg_price_month / eve_items.cost - 1.0
        (NULL when cost is NULL)

    WHEN DATA CHANGES
    -----------------
    prices_advices and prices_mins are both updated every ~15 minutes by
    process/orders_daemon.py and once per run of process/hourly.py.
    process/daily.py also calls update_prices_advices_immediate() after
    recomputing weekly/monthly history stats.
    Being a plain SQL VIEW, results are live immediately after the underlying
    tables change.

    WHERE IT IS USED
    ----------------
    - evebs/routes/price_advices.py  →  GET /price_advices/empty_places
        Finds items with monthly volume but no current min_price (market gap detection).
    - evebs/routes/market_data.py  →  GET /market_data
        Sorts items by volume and margin for the market data dashboard.
    """

    __tablename__ = 'price_advices_min_prices'
    __table_args__ = {'info': {'is_view': True}}

    id = db.Column(db.Integer, primary_key=True)
    eve_item_id = db.Column(db.Integer)
    trade_hub_id = db.Column(db.Integer)
    trade_hub_name = db.Column(db.String)           # "SystemName (RegionName)"
    item_name = db.Column(db.String)
    cost = db.Column(db.Float)                      # manufacturing cost from eve_items
    min_price = db.Column(db.Float)                 # current min sell price (nullable)
    avg_price_week = db.Column(db.Float)            # 7-day weighted average price
    avg_price_month = db.Column(db.Float)           # 30-day average price
    vol_month = db.Column(db.BigInteger)            # 30-day sales volume
    full_batch_size = db.Column(db.Integer)         # nb_runs × prod_qtt
    immediate_montly_pcent = db.Column(db.Float)    # min_price as % of monthly avg
    margin_percent = db.Column(db.Float)            # stored margin % from prices_advices
    avg_monthly_margin_percent = db.Column(db.Float)  # avg_price_month / cost - 1.0

    eve_item = db.relationship('EveItem', foreign_keys=[eve_item_id],
                               primaryjoin='PriceAdvicesMinPrice.eve_item_id == EveItem.id',
                               viewonly=True)
