from evebs.extensions import db


class JitaReactionMargins(db.Model):
    """PostgreSQL materialized view: jita_reaction_margins.

    Computes the theoretical profit from buying all reaction inputs at Jita and
    selling the reaction output at Jita, for every reaction-type blueprint in the
    database.  Mirrors jita_manufacturing_margins but for reaction formulas, and
    notably omits the manufacturing tax (reactions do not incur a 10% industry tax).

    HOW IT IS COMPUTED
    ------------------
    Source tables:
      - blueprints            – reaction formulas (activity_type = 'reaction'),
                                seeded from blueprints.jsonl activities.reaction
      - blueprint_materials   – required inputs per reaction formula
      - eve_items             – to look up material item IDs
      - jita_prices           – Jita price oracle (MUST be refreshed first)

    Formula:
      reaction_cost          = SUM(required_qtt × jita_prices.min_sell_price)
                                 over all input materials
      estimated_selling_price= prod_qtt × jita_prices.min_sell_price  (output item)
      selling_tax            = estimated_selling_price × 0.05  (5% broker/sales tax)
      benefit                = estimated_selling_price
                               - selling_tax
                               - reaction_cost
                               (no manufacturing tax, unlike jita_manufacturing_margins)

    Only blueprints with activity_type = 'reaction' are included (created in
    migration f0f0056bec00 alongside the activity_type column).

    WHEN IT IS REFRESHED
    --------------------
    Materialized: results are FROZEN until explicitly refreshed.

    Dependency: jita_prices must be refreshed BEFORE this view.

    Refresh script: process/update_jita_reaction_margins.py
      python process/update_jita_reaction_margins.py      # refresh
      python process/update_jita_reaction_margins.py -n   # dry-run: print row count

    Intended cadence: after process/update_jita_prices.py completes,
    alongside process/update_jita_manufacturing_margins.py.
    (Must be run manually or via cron.)

    WHERE IT IS USED
    ----------------
    - evebs/routes/jita_reactions.py  →  GET /jita_reactions
        Filters rows to reaction formulas owned by current_user (via
        user_blueprints association), benefit IS NOT NULL, sorted by benefit
        descending.  Shows only the profitable reactions for the user's owned
        reaction formulas.  Refresh button on this page calls
        esi/download_my_blueprints.py to sync owned formulas from ESI.
    """

    __tablename__ = 'jita_reaction_margins'
    __table_args__ = {'info': {'is_view': True}}

    id                      = db.Column(db.BigInteger, primary_key=True)  # = produced_type_id
    eve_item_id             = db.Column(db.Integer, db.ForeignKey('eve_items.id'))
    reaction_cost           = db.Column(db.Float)   # total input cost at Jita
    estimated_selling_price = db.Column(db.Float)   # prod_qtt × Jita min_sell_price
    selling_tax             = db.Column(db.Float)   # 5% of estimated_selling_price
    benefit                 = db.Column(db.Float)   # net profit (no manufacturing tax)

    eve_item = db.relationship('EveItem', foreign_keys=[eve_item_id])
