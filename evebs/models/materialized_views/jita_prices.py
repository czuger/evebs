from evebs.extensions import db


class JitaPrices(db.Model):
    """PostgreSQL materialized view: jita_prices.

    Computes robust buy and sell price benchmarks for every item that has active
    orders at Jita (system 30000142), filtering out thin-volume outliers via
    cumulative-volume percentile cuts.  Acts as the price oracle for both
    jita_manufacturing_margins and jita_reaction_margins.

    HOW IT IS COMPUTED
    ------------------
    Source tables:
      - public_trade_orders  – live market orders, updated every ~15 min by
                               process/orders_daemon.py / process/hourly.py
      - universe_systems     – to look up Jita by cpp_system_id = 30000142

    Algorithm (all restricted to Jita):

      sell_p10 — minimum sell price after skipping the bottom 10% of volume:
        For each item, sort sell orders ascending by price.  Walk orders until
        cumulative volume ≥ 10% of total sell volume.  Take the price at that
        point as min_sell_price.  This ignores small "bait" listings that are
        never actually filled.

      buy_p90 — deflated maximum buy price ignoring the top 10% of volume:
        For each item, sort buy orders ascending (cheapest first), walk until
        cumulative volume ≥ 90% of total buy volume, then multiply that price
        by 0.9.  Represents a conservative immediate-sell estimate.

      spread = min_sell_price - max_buy_price
        → the arbitrage gap between buying cheap and selling high at Jita.

    Columns that have no orders produce NULL (LEFT JOIN from union of item IDs).

    WHEN IT IS REFRESHED
    --------------------
    Materialized: results are FROZEN until explicitly refreshed.

    Refresh script: process/update_jita_prices.py
      python process/update_jita_prices.py      # refresh
      python process/update_jita_prices.py -n   # dry-run: print row count only

    Intended cadence: after each public_trade_orders update, i.e. after
    process/orders_daemon.py completes a cycle or after process/hourly.py.
    (Must be run manually or via cron — not yet auto-wired into those scripts.)

    WHERE IT IS USED
    ----------------
    - evebs/models/materialized_views/jita_manufacturing_margins.py
        JitaManufacturingMargins joins this view for both material costs and
        the estimated selling price of the produced item.
    - evebs/models/materialized_views/jita_reaction_margins.py
        JitaReactionMargins does the same for reaction-formula blueprints.
    - process/update_eve_item_costs.py::update_eve_item_cost()
        Reads the top-10 sell orders directly from public_trade_orders (not
        this view) to compute eve_items.cost — does NOT depend on jita_prices.
    """

    __tablename__ = 'jita_prices'
    __table_args__ = {'info': {'is_view': True}}

    id             = db.Column(db.BigInteger, primary_key=True)  # EVE item type_id
    min_sell_price = db.Column(db.Float)   # 10th-percentile-volume ask price at Jita
    max_buy_price  = db.Column(db.Float)   # 90th-percentile-volume bid × 0.9 at Jita
    spread         = db.Column(db.Float)   # min_sell_price - max_buy_price
