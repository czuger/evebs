"""SQL view definitions — parked here for rework. Not currently used."""


def _create_views():
    from sqlalchemy import text
    conn = db.engine.connect()

    views = [
        ("buy_orders_analytics_results", """
            SELECT boa.id,
              u.id AS user_id,
              boa.system_id,
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
            JOIN universe_types ei ON ei.id = boa.eve_item_id
            JOIN universe_systems tu ON boa.system_id = tu.id
            JOIN universe_systems_users thu ON boa.system_id = thu.universe_system_id
            JOIN eve_items_users eiu ON boa.eve_item_id = eiu.eve_item_id
            JOIN users u ON thu.user_id = u.id AND eiu.user_id = u.id
            JOIN universe_regions r ON tu.region_id = r.id
            JOIN blueprints bp ON bp.produced_type_id = ei.id
            WHERE boa.over_approx_max_price_volume > 0
        """),
        ("price_advices_min_prices", """
            SELECT pa.id,
              ei.id AS eve_item_id,
              tu.id AS system_id,
              (tu.name || ' (' || re.name || ')') AS trade_hub_name,
              ei.name AS item_name,
              ei.cost,
              pm.p10_price AS min_price,
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
            JOIN universe_types ei ON pa.eve_item_id = ei.id
            JOIN blueprints bp ON bp.produced_type_id = ei.id
            JOIN universe_systems tu ON pa.system_id = tu.id
            JOIN universe_regions re ON re.id = tu.region_id
            LEFT JOIN market_seller_prices pm ON pm.type_id = ei.id
              AND pm.system_id = tu.eve_system_id
        """),
        ("user_sale_order_details", """
            SELECT uso.id,
              uso.user_id,
              (tu.name || ' (' || r.name || ')') AS trade_hub_name,
              ei.name AS eve_item_name,
              uso.price AS my_price,
              pm.p10_price AS min_price,
              ei.cost,
              b.prod_qtt,
              (pm.p10_price / ei.cost - 1.0) AS min_price_margin_pcent,
              (pm.p10_price - uso.price) AS price_delta,
              uso.eve_item_id,
              uso.system_id,
              ei.id AS cpp_eve_item_id,
              tu.eve_system_id
            FROM user_sale_orders uso
            JOIN universe_types ei ON ei.id = uso.eve_item_id
            JOIN blueprints b ON b.produced_type_id = ei.id
            JOIN universe_systems tu ON uso.system_id = tu.id
            JOIN universe_regions r ON tu.region_id = r.id
            LEFT JOIN market_seller_prices pm ON pm.type_id = uso.eve_item_id
              AND pm.system_id = tu.eve_system_id
        """),
        ("price_advice_margin_comps", """
            SELECT pa.id,
              ur.id AS user_id,
              ei.id AS item_id,
              tu.id AS system_id,
              re.name AS region_name,
              tu.name AS trade_hub_name,
              ei.name AS item_name,
              ei.cost AS single_unit_cost,
              pm.p10_price AS min_price,
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
              (pm.p10_price * CASE
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
            JOIN universe_types ei ON pa.eve_item_id = ei.id
            JOIN blueprints bp ON bp.produced_type_id = ei.id
            JOIN universe_systems tu ON pa.system_id = tu.id
            JOIN universe_regions re ON re.id = tu.region_id
            JOIN universe_systems_users thu ON thu.universe_system_id = pa.system_id
            JOIN eve_items_users eiu ON eiu.eve_item_id = pa.eve_item_id
            JOIN users ur ON thu.user_id = ur.id AND eiu.user_id = ur.id
            JOIN market_seller_prices pm ON pm.type_id = ei.id
              AND pm.system_id = tu.eve_system_id
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
            JOIN universe_types ei ON ei.id = pl.eve_item_id
            JOIN blueprints b ON b.produced_type_id = ei.id
            JOIN blueprint_materials bm ON b.id = bm.blueprint_id
            JOIN universe_types bpm_mat_ei ON bm.universe_type_id = bpm_mat_ei.id
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
