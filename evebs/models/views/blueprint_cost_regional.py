from evebs.extensions import db


class BlueprintCostRegional(db.Model):
    """Read-only view: production cost and margin per (blueprint, region).

    Regional prices aggregate across all systems in a region:
      material costs  — MIN(p10_price) per material type (cheapest sell in region)
      output revenue  — MAX(p90_price) for produced item (best buy offer in region)

    Column suffix convention matches BlueprintCost:
      _sell  — derived from sell orders (market_seller_prices p10)
      _buy   — derived from buy orders  (market_buyer_prices  p90)
    """

    __tablename__ = 'blueprint_cost_regional'
    __table_args__ = {'info': {'is_view': True}}

    blueprint_id  = db.Column(db.BigInteger, primary_key=True)
    region_id     = db.Column(db.BigInteger, primary_key=True)

    blueprint_name       = db.Column(db.Text)
    produced_type_id     = db.Column(db.BigInteger)
    region_name          = db.Column(db.Text)

    nb_runs              = db.Column(db.Integer)
    prod_qtt             = db.Column(db.Integer)
    batch_elements_count = db.Column(db.Integer)

    material_cost_sell   = db.Column(db.Float)
    cost_per_unit_sell   = db.Column(db.Float)

    material_value_buy   = db.Column(db.Float)
    value_per_unit_buy   = db.Column(db.Float)

    output_price_buy     = db.Column(db.Float)
    batch_revenue_buy    = db.Column(db.Float)
    output_volume_buy    = db.Column(db.BigInteger)

    margin_per_unit      = db.Column(db.Float)
    craft_vs_sell_margin = db.Column(db.Float)
    roi_percent          = db.Column(db.Float)

    has_missing_prices   = db.Column(db.Boolean)
    material_line_count  = db.Column(db.Integer)
