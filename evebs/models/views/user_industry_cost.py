from evebs.extensions import db


class UserIndustryCost(db.Model):
    """Read-only SQL view: user_industry_costs.

    One row per (user, blueprint) combination. Computes per-unit manufacturing or
    reaction cost live from JitaMinPrice prices and the user's personal
    User.industry_modifications settings.

    Only blueprints where EVERY direct material has a JMA price are included
    (incomplete-price blueprints are silently excluded by the view's HAVING clause).

    Additional derived columns (not stored in the view) are computed at query time:
      total_cost_per_unit = mat_cost_per_unit + ind_tax_per_unit
      margin_per_unit     = jita_sell_price   - total_cost_per_unit
    """

    __tablename__ = 'user_industry_costs'
    __table_args__ = {'info': {'is_view': True}}

    user_id          = db.Column(db.Integer,   primary_key=True)
    user_name        = db.Column(db.String)
    blueprint_id     = db.Column(db.Integer,   primary_key=True)
    produced_type_id = db.Column(db.Integer)
    activity_type    = db.Column(db.String)
    blueprint_name   = db.Column(db.String)
    item_name        = db.Column(db.String)
    item_slug        = db.Column(db.String)
    mat_cost_per_unit = db.Column(db.Float)   # raw material cost / prod_qtt
    ind_tax_per_unit  = db.Column(db.Float)   # industry tax portion (SCI + SCC + activity tax)
    jita_sell_price   = db.Column(db.Float)   # JMA min_sell_price for the produced item
