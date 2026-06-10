from evebs.extensions import db


class UserBlueprintExtended(db.Model):
    """Read-only SQL view: user_blueprint_extended.

    One row per (user, blueprint) entry in user_blueprints, with all foreign-key
    IDs resolved to their human-readable names.

    Columns:
      id               – user_blueprints.id (surrogate PK)
      user_id          – FK to users
      user_name        – users.name
      blueprint_id     – FK to blueprints
      blueprint_name   – blueprints.name
      activity_type    – 'manufacturing' | 'reaction' | …
      produced_type_id – FK to eve_items (the item the blueprint produces)
      item_name        – eve_items.name of the produced item
      item_slug        – eve_items.slug of the produced item
      market_group_id  – FK to market_groups (NULL if no group)
      market_group_name – market_groups.name (NULL if no group)
      nb_runs          – blueprints.nb_runs
      prod_qtt         – blueprints.prod_qtt
      manufacturing_cost – blueprints.manufacturing_cost (NULL if not computed yet)
    """

    __tablename__ = 'user_blueprint_extended'
    __table_args__ = {'info': {'is_view': True}}

    id               = db.Column(db.Integer,  primary_key=True)
    user_id          = db.Column(db.Integer)
    user_name        = db.Column(db.String)
    blueprint_id     = db.Column(db.Integer)
    blueprint_name   = db.Column(db.String)
    activity_type    = db.Column(db.String)
    produced_type_id = db.Column(db.Integer)
    item_name        = db.Column(db.String)
    item_slug        = db.Column(db.String)
    market_group_id  = db.Column(db.Integer)
    market_group_name = db.Column(db.String)
    nb_runs          = db.Column(db.Integer)
    prod_qtt         = db.Column(db.Integer)
    manufacturing_cost = db.Column(db.Float)
