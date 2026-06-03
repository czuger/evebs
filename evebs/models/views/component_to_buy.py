from evebs.extensions import db


class ComponentToBuy(db.Model):
    """Read-only SQL view: components_to_buys.

    Aggregates the raw materials needed across all of a user's active production
    runs (production_lists), applies any per-user blueprint modifications
    (efficiency improvements), and subtracts stock the user already holds at
    their selected assets station.  Only rows where the net quantity to buy
    is still positive appear (HAVING clause).

    HOW IT IS COMPUTED
    ------------------
    Source tables:
      - production_lists      – user's items to produce with run counts;
                                managed via POST /production_lists (create/update/delete)
      - blueprints            – blueprint that produces the item
      - blueprint_materials   – list of input materials per blueprint
      - blueprint_modifications – optional per-user material efficiency factor
                                  (COALESCE to 1.0 when absent)
      - eve_items             – material metadata (name, cost, volume)
      - users                 – for selected_assets_station_id (deduction station)
      - bpc_assets            – user's existing stock; LEFT JOINed on
                                bpc_assets.universe_station_id = users.selected_assets_station_id
                                so deduction only applies when the user has set a station

    Quantity formula per material:
      qtt_to_buy = SUM(CEIL(required_qtt × runs_count × modification_factor))
                   - COALESCE(bpc_assets.quantity, 0)

    Grouping: per (user_id, material eve_item_id)
    Filter (HAVING): qtt_to_buy > 0  → only items still needed appear

    WHEN DATA CHANGES
    -----------------
    This is a plain SQL VIEW — results update instantly when any underlying
    table changes:
      - Adding/removing/updating a production_list entry immediately changes
        which materials appear and in what quantities.
      - Syncing assets (POST /my_assets/sync) updates bpc_assets, which
        adjusts the deduction against the selected station.
      - Setting a default station (POST /my_assets/set_assets_station) changes
        which station's stock is subtracted, taking effect on the next page load.
      - eve_items.cost is updated daily by process/daily.py via
        process/update_costs.py::update_all_costs() — affects total_cost column.

    WHERE IT IS USED
    ----------------
    - evebs/routes/components_to_buys.py  →  GET /components_to_buys
        Filters: user_id = current_user.id
        Optionally further subtracts a user-chosen station's stock (route-level
        query on bpc_assets, independent of the view's built-in deduction).
        Displayed as a shopping list with an EVE multi-buy paste option.
    """

    __tablename__ = 'components_to_buys'
    __table_args__ = {'info': {'is_view': True}}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    eve_item_name = db.Column(db.String)
    eve_item_id = db.Column(db.Integer)
    qtt_to_buy = db.Column(db.Float)       # net quantity after deducting station stock
    total_cost = db.Column(db.Float)       # qtt_to_buy × eve_items.cost
    required_volume = db.Column(db.Float)  # qtt_to_buy × eve_items.volume (m³)
    base_item = db.Column(db.Boolean)      # True = raw material (not manufactured)
