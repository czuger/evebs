from evebs.extensions import db


class BlueprintCost(db.Model):
    """Read-only view: pre-computed production cost and margin per (blueprint, system).

    Column suffix convention:
      _sell  — derived from sell orders (market_seller_prices p10): what you pay to acquire
      _buy   — derived from buy orders  (market_buyer_prices  p90): what you receive when selling
    """

    __tablename__ = 'blueprint_costs'
    __table_args__ = {'info': {'is_view': True}}

    blueprint_id = db.Column(db.BigInteger, primary_key=True)
    system_id    = db.Column(db.BigInteger, primary_key=True)

    blueprint_name      = db.Column(db.Text)
    produced_type_id    = db.Column(db.BigInteger)
    system_name         = db.Column(db.Text)

    nb_runs              = db.Column(db.Integer)
    prod_qtt             = db.Column(db.Integer)
    batch_elements_count = db.Column(db.Integer)

    # Cost to buy all materials via sell orders
    material_cost_sell = db.Column(db.Float)
    cost_per_unit_sell = db.Column(db.Float)

    # Value of materials if sold via buy orders (opportunity cost)
    material_value_buy = db.Column(db.Float)
    value_per_unit_buy = db.Column(db.Float)

    # Revenue from selling the produced item via buy orders
    output_price_buy   = db.Column(db.Float)
    batch_revenue_buy  = db.Column(db.Float)
    output_volume_buy  = db.Column(db.BigInteger)

    # Margins
    margin_per_unit     = db.Column(db.Float)   # output_price_buy - cost_per_unit_sell
    craft_vs_sell_margin = db.Column(db.Float)  # output_price_buy - value_per_unit_buy
    roi_percent         = db.Column(db.Float)   # margin_per_unit / cost_per_unit_sell × 100

    has_missing_prices  = db.Column(db.Boolean)
    material_line_count = db.Column(db.Integer)
