from evebs.extensions import db


class PriceAdviceMarginComp(db.Model):
    """Read-only SQL view: price_advice_margin_comps.

    Per-user price advice with two computed profit figures — one using the current
    minimum market price (immediate) and one using the 7-day average price (weekly).
    Accounts for the user's personal batch-cap settings and minimum thresholds.
    Only items the user is watching at one of their trade hubs appear here.

    HOW IT IS COMPUTED
    ------------------
    Source tables:
      - prices_advices   – weekly/monthly price statistics per item/hub
      - prices_mins      – current minimum sell price per item/hub
      - eve_items        – item metadata (cost, weekly_avg_price)
      - blueprints       – batch size (nb_runs × prod_qtt)
      - universe_*       – human-readable names
      - trade_hubs_users – user's selected trade hubs
      - eve_items_users  – user's watched items
      - users            – user thresholds: batch_cap, batch_cap_multiplier,
                           vol_month_pcent, min_amount_for_advice, min_pcent_for_advice

    Key derived columns:
      batch_size_formula:
        If user.batch_cap is True:
          MIN(nb_runs × prod_qtt × batch_cap_multiplier,
              FLOOR(vol_month × vol_month_pcent / 100))
        Else:
          FLOOR(vol_month × vol_month_pcent / 100)

      margin_comp_immediate = batch_size_formula × (min_price - cost)
        → ISK profit if selling at today's minimum price
      margin_comp_weekly    = batch_size_formula × (weekly_avg_price - cost)
        → ISK profit if selling at the 7-day average price

    WHEN DATA CHANGES
    -----------------
    prices_advices and prices_mins are refreshed every ~15 minutes by
    process/orders_daemon.py (and once per run of process/hourly.py and
    process/daily.py).  Being a plain SQL VIEW, results are live immediately.

    WHERE IT IS USED
    ----------------
    - evebs/routes/price_advices.py  →  GET /price_advices/advice_prices
        Shows "immediate" advice: sorted by margin_comp_immediate descending.
        Filters: user_id, margin_comp_immediate ≥ user.min_amount_for_advice,
                 margin_percent ≥ user.min_pcent_for_advice.
    - evebs/routes/price_advices.py  →  GET /price_advices/advice_prices_weekly
        Shows "weekly" advice: sorted by margin_comp_weekly descending.
        Same filters applied against weekly column.
    """

    __tablename__ = 'price_advice_margin_comps'
    __table_args__ = {'info': {'is_view': True}}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    item_id = db.Column(db.Integer)
    trade_hub_id = db.Column(db.Integer)
    region_name = db.Column(db.String)
    trade_hub_name = db.Column(db.String)
    item_name = db.Column(db.String)
    single_unit_cost = db.Column(db.Float)          # manufacturing cost per unit
    min_price = db.Column(db.Float)                 # current min sell price
    price_avg_week = db.Column(db.Float)            # 7-day weighted average price
    vol_month = db.Column(db.BigInteger)            # 30-day sales volume
    full_batch_size = db.Column(db.Integer)         # nb_runs × prod_qtt
    daily_monthly_pcent = db.Column(db.Float)       # min_price as % of monthly avg
    margin_percent = db.Column(db.Float)            # stored margin % from prices_advices
    batch_size_formula = db.Column(db.Float)        # user-capped batch size (see above)
    min_amount_for_advice = db.Column(db.Integer)   # user's ISK threshold
    min_pcent_for_advice = db.Column(db.Integer)    # user's margin % threshold
    margin_comp_immediate = db.Column(db.Float)     # ISK profit at min_price
    margin_comp_weekly = db.Column(db.Float)        # ISK profit at weekly avg price
