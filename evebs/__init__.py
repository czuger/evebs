from flask import Flask
from config import Config
from evebs.extensions import db, migrate, login_manager
from evebs import helpers


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    helpers.register(app)

    from evebs.routes.auth import bp as auth_bp
    from evebs.routes.main import bp as main_bp
    from evebs.routes.buy_orders import bp as buy_orders_bp
    from evebs.routes.price_advices import bp as price_advices_bp
    from evebs.routes.items import bp as items_bp
    from evebs.routes.list_items import bp as list_items_bp
    from evebs.routes.production_costs import bp as production_costs_bp
    from evebs.routes.production_lists import bp as production_lists_bp
    from evebs.routes.user_sales_orders import bp as user_sales_orders_bp
    from evebs.routes.users import bp as users_bp
    from evebs.routes.choose_trade_hubs import bp as choose_trade_hubs_bp
    from evebs.routes.components_to_buys import bp as components_to_buys_bp
    from evebs.routes.market_data import bp as market_data_bp
    from evebs.routes.market_groups import bp as market_groups_bp
    from evebs.routes.eve_items_saved_lists import bp as eve_items_saved_lists_bp
    from evebs.routes.my_assets import bp as my_assets_bp
    from evebs.routes.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(buy_orders_bp)
    app.register_blueprint(price_advices_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(list_items_bp)
    app.register_blueprint(production_costs_bp)
    app.register_blueprint(production_lists_bp)
    app.register_blueprint(user_sales_orders_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(choose_trade_hubs_bp)
    app.register_blueprint(components_to_buys_bp)
    app.register_blueprint(market_data_bp)
    app.register_blueprint(market_groups_bp)
    app.register_blueprint(eve_items_saved_lists_bp)
    app.register_blueprint(my_assets_bp)
    app.register_blueprint(admin_bp)

    return app


def _create_views():
    from sqlalchemy import text
    conn = db.engine.connect()

    views = [
        ("buy_orders_analytics_results", """
            SELECT boa.id,
              u.id AS user_id,
              boa.trade_hub_id,
              boa.eve_item_id,
              (tu.name || ' (' || r.name || ')') AS trade_hub_name,
              ei.name AS eve_item_name,
              boa.over_approx_max_price_volume,
              boa.approx_max_price,
              boa.single_unit_cost,
              boa.single_unit_margin,
              (1.0 - (boa.single_unit_cost / boa.approx_max_price)) AS margin_pcent,
              (boa.over_approx_max_price_volume * boa.single_unit_margin) AS full_margin,
              (bp.nb_runs * bp.prod_qtt * u.batch_cap_multiplier) AS batch_cap,
              LEAST(CAST(boa.over_approx_max_price_volume AS REAL),
                  CAST(bp.nb_runs * bp.prod_qtt * u.batch_cap_multiplier AS REAL)) AS capped_volume,
              (LEAST(CAST(boa.over_approx_max_price_volume AS REAL),
                   CAST(bp.nb_runs * bp.prod_qtt * u.batch_cap_multiplier AS REAL))
               * boa.single_unit_margin) AS capped_margin
            FROM buy_orders_analytics boa
            JOIN eve_items ei ON ei.id = boa.eve_item_id
            JOIN trade_hubs tu ON boa.trade_hub_id = tu.id
            JOIN trade_hubs_users thu ON boa.trade_hub_id = thu.trade_hub_id
            JOIN eve_items_users eiu ON boa.eve_item_id = eiu.eve_item_id
            JOIN users u ON thu.user_id = u.id AND eiu.user_id = u.id
            JOIN universe_regions r ON tu.region_id = r.id
            JOIN blueprints bp ON ei.blueprint_id = bp.id
            WHERE boa.over_approx_max_price_volume > 0
        """),
        ("price_advices_min_prices", """
            SELECT pa.id,
              ei.id AS eve_item_id,
              tu.id AS trade_hub_id,
              (tu.name || ' (' || re.name || ')') AS trade_hub_name,
              ei.name AS item_name,
              ei.cost,
              pm.min_price,
              pa.avg_price_week,
              pa.avg_price_month,
              pa.vol_month,
              (bp.nb_runs * bp.prod_qtt) AS full_batch_size,
              pa.immediate_montly_pcent,
              pa.margin_percent,
              CASE
                WHEN ei.cost IS NULL THEN NULL
                ELSE (pa.avg_price_month / ei.cost - 1.0)
              END AS avg_monthly_margin_percent
            FROM prices_advices pa
            JOIN eve_items ei ON pa.eve_item_id = ei.id
            JOIN blueprints bp ON ei.blueprint_id = bp.id
            JOIN trade_hubs tu ON pa.trade_hub_id = tu.id
            JOIN universe_regions re ON re.id = tu.region_id
            LEFT JOIN prices_mins pm ON pm.trade_hub_id = pa.trade_hub_id
              AND pa.eve_item_id = pm.eve_item_id
        """),
        ("user_sale_order_details", """
            SELECT uso.id,
              uso.user_id,
              (tu.name || ' (' || r.name || ')') AS trade_hub_name,
              ei.name AS eve_item_name,
              uso.price AS my_price,
              pm.min_price,
              ei.cost,
              b.prod_qtt,
              (pm.min_price / ei.cost - 1.0) AS min_price_margin_pcent,
              (pm.min_price - uso.price) AS price_delta,
              uso.eve_item_id,
              uso.trade_hub_id,
              ei.cpp_eve_item_id,
              tu.eve_system_id
            FROM user_sale_orders uso
            JOIN eve_items ei ON ei.id = uso.eve_item_id
            JOIN blueprints b ON ei.blueprint_id = b.id
            JOIN trade_hubs tu ON uso.trade_hub_id = tu.id
            JOIN universe_regions r ON tu.region_id = r.id
            LEFT JOIN prices_mins pm ON pm.eve_item_id = uso.eve_item_id
              AND pm.trade_hub_id = uso.trade_hub_id
        """),
        ("price_advice_margin_comps", """
            SELECT pa.id,
              ur.id AS user_id,
              ei.id AS item_id,
              tu.id AS trade_hub_id,
              re.name AS region_name,
              tu.name AS trade_hub_name,
              ei.name AS item_name,
              ei.cost AS single_unit_cost,
              pm.min_price,
              ei.weekly_avg_price AS price_avg_week,
              pa.vol_month,
              (bp.nb_runs * bp.prod_qtt) AS full_batch_size,
              pa.immediate_montly_pcent AS daily_monthly_pcent,
              pa.margin_percent,
              CASE
                WHEN ur.batch_cap THEN LEAST(
                  CAST(bp.nb_runs * bp.prod_qtt * ur.batch_cap_multiplier AS REAL),
                  CAST(floor(pa.vol_month * ur.vol_month_pcent * 0.01) AS REAL))
                ELSE CAST(floor(pa.vol_month * ur.vol_month_pcent * 0.01) AS REAL)
              END AS batch_size_formula,
              ur.min_amount_for_advice,
              ur.min_pcent_for_advice,
              (pm.min_price * CASE
                WHEN ur.batch_cap THEN LEAST(
                  CAST(bp.nb_runs * bp.prod_qtt * ur.batch_cap_multiplier AS REAL),
                  CAST(floor(pa.vol_month * ur.vol_month_pcent * 0.01) AS REAL))
                ELSE CAST(floor(pa.vol_month * ur.vol_month_pcent * 0.01) AS REAL)
              END
              - ei.cost * CASE
                WHEN ur.batch_cap THEN LEAST(
                  CAST(bp.nb_runs * bp.prod_qtt * ur.batch_cap_multiplier AS REAL),
                  CAST(floor(pa.vol_month * ur.vol_month_pcent * 0.01) AS REAL))
                ELSE CAST(floor(pa.vol_month * ur.vol_month_pcent * 0.01) AS REAL)
              END) AS margin_comp_immediate,
              (ei.weekly_avg_price * CASE
                WHEN ur.batch_cap THEN LEAST(
                  CAST(bp.nb_runs * bp.prod_qtt * ur.batch_cap_multiplier AS REAL),
                  CAST(floor(pa.vol_month * ur.vol_month_pcent * 0.01) AS REAL))
                ELSE CAST(floor(pa.vol_month * ur.vol_month_pcent * 0.01) AS REAL)
              END
              - ei.cost * CASE
                WHEN ur.batch_cap THEN LEAST(
                  CAST(bp.nb_runs * bp.prod_qtt * ur.batch_cap_multiplier AS REAL),
                  CAST(floor(pa.vol_month * ur.vol_month_pcent * 0.01) AS REAL))
                ELSE CAST(floor(pa.vol_month * ur.vol_month_pcent * 0.01) AS REAL)
              END) AS margin_comp_weekly
            FROM prices_advices pa
            JOIN eve_items ei ON pa.eve_item_id = ei.id
            JOIN blueprints bp ON ei.blueprint_id = bp.id
            JOIN trade_hubs tu ON pa.trade_hub_id = tu.id
            JOIN universe_regions re ON re.id = tu.region_id
            JOIN trade_hubs_users thu ON thu.trade_hub_id = pa.trade_hub_id
            JOIN eve_items_users eiu ON eiu.eve_item_id = pa.eve_item_id
            JOIN users ur ON thu.user_id = ur.id AND eiu.user_id = ur.id
            JOIN prices_mins pm ON pm.trade_hub_id = pa.trade_hub_id
              AND pa.eve_item_id = pm.eve_item_id
            WHERE pa.vol_month IS NOT NULL
        """),
        ("components_to_buys", """
            SELECT bpm_mat_ei.id,
              pl.user_id,
              bpm_mat_ei.name AS eve_item_name,
              bpm_mat_ei.id AS eve_item_id,
              (SUM(ceil(bm.required_qtt * pl.runs_count *
                COALESCE(bmo.percent_modification_value, 1.0)))
                - COALESCE(ba.quantity, 0)) AS qtt_to_buy,
              ((SUM(ceil(bm.required_qtt * pl.runs_count *
                COALESCE(bmo.percent_modification_value, 1.0)))
                - COALESCE(ba.quantity, 0)) * bpm_mat_ei.cost) AS total_cost,
              ((SUM(ceil(bm.required_qtt * pl.runs_count *
                COALESCE(bmo.percent_modification_value, 1.0)))
                - COALESCE(ba.quantity, 0)) * bpm_mat_ei.volume) AS required_volume,
              bpm_mat_ei.base_item
            FROM production_lists pl
            JOIN eve_items ei ON ei.id = pl.eve_item_id
            JOIN blueprints b ON ei.blueprint_id = b.id
            JOIN blueprint_materials bm ON b.id = bm.blueprint_id
            JOIN eve_items bpm_mat_ei ON bm.universe_type_id = bpm_mat_ei.id
            JOIN users ue ON pl.user_id = ue.id
            LEFT JOIN blueprint_modifications bmo
              ON b.id = bmo.blueprint_id AND bmo.user_id = pl.user_id
            LEFT JOIN bpc_assets ba
              ON bpm_mat_ei.id = ba.eve_item_id
              AND ba.universe_station_id = ue.selected_assets_station_id
            WHERE pl.runs_count > 0
            GROUP BY bpm_mat_ei.id, pl.user_id, bpm_mat_ei.name,
              COALESCE(ba.quantity, 0), bpm_mat_ei.cost, bpm_mat_ei.volume,
              bpm_mat_ei.base_item
            HAVING (SUM(ceil(bm.required_qtt * pl.runs_count *
              COALESCE(bmo.percent_modification_value, 1.0)))
              - COALESCE(ba.quantity, 0)) > 0
        """),
    ]

    for view_name, select_sql in views:
        conn.execute(text(f"DROP VIEW IF EXISTS {view_name}"))
        conn.execute(text(f"CREATE VIEW {view_name} AS {select_sql}"))

    conn.commit()
    conn.close()
