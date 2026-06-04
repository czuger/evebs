from evebs.extensions import db


class JitaManufacturingMargins(db.Model):
    """PostgreSQL materialized view: jita_manufacturing_margins.

    Computes the theoretical profit from buying all required materials at Jita
    and selling the manufactured product at Jita, for every manufacturing-type
    blueprint in the database.  One row per blueprint/product.

    HOW IT IS COMPUTED
    ------------------
    Source tables:
      - blueprints   – manufacturing blueprints (activity_type = 'manufacturing');
                       manufacturing_cost column pre-computed by process/update_blueprints.py
                       as SUM(material_qty × jita_prices.min_sell_price) at the time of the
                       last blueprint update run.
      - eve_items    – to resolve the produced item's DB id
      - jita_prices  – Jita price oracle for the OUTPUT item only (MUST be refreshed first)

    Formula (all derived from Blueprint.manufacturing_cost):
      manufacturing_tax      = blueprints.manufacturing_cost × 0.10  (10% facility tax)
      estimated_selling_price= prod_qtt × jita_prices.min_sell_price  (output item)
      selling_tax            = estimated_selling_price × 0.05  (5% broker/sales tax)
      benefit                = estimated_selling_price
                               - selling_tax
                               - manufacturing_cost
                               - manufacturing_tax

    Rows with manufacturing_cost IS NULL are excluded (materials had no Jita price
    when update_blueprints.py last ran).  Only activity_type = 'manufacturing'.

    WHEN IT IS REFRESHED
    --------------------
    Materialized: results are FROZEN until explicitly refreshed.

    Dependency: jita_prices must be refreshed BEFORE this view, because this view
    reads jita_prices directly.

    Refresh script: process/update_jita_manufacturing_margins.py
      python process/update_jita_manufacturing_margins.py      # refresh
      python process/update_jita_manufacturing_margins.py -n   # dry-run: print row count

    Intended cadence: after process/update_jita_prices.py completes.
    (Must be run manually or via cron.)

    WHERE IT IS USED
    ----------------
    - evebs/routes/jita_manufacturing.py  →  GET /jita_manufacturing
        Filters rows to blueprints owned by current_user (via user_blueprints
        association), benefit IS NOT NULL, sorted by benefit descending.
        Shows each user only the profitable manufacturing chains for their
        owned blueprints.
    - evebs/routes/jita_benefits.py  →  GET /jita_benefits
        Market-wide view (no user filter): all manufacturing blueprints with
        benefit > 0, sorted by benefit descending.
    """

    __tablename__ = 'jita_manufacturing_margins'
    __table_args__ = {'info': {'is_view': True}}

    id                      = db.Column(db.BigInteger, primary_key=True)  # = produced_type_id
    eve_item_id             = db.Column(db.Integer, db.ForeignKey('eve_items.id'))
    manufacturing_cost      = db.Column(db.Float)   # total material cost at Jita
    manufacturing_tax       = db.Column(db.Float)   # 10% of manufacturing_cost
    estimated_selling_price = db.Column(db.Float)   # prod_qtt × Jita min_sell_price
    selling_tax             = db.Column(db.Float)   # 5% of estimated_selling_price
    benefit                 = db.Column(db.Float)   # net profit after all taxes

    eve_item = db.relationship('EveItem', foreign_keys=[eve_item_id])
