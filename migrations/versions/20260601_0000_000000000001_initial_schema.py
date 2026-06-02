"""Initial schema — full database from scratch.

Revision ID: 000000000001
Revises:
Create Date: 2026-06-01
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = '000000000001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- leaf / no-dep tables ---
    op.create_table(
        'constants',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('libe', sa.String(), nullable=False, unique=True),
        sa.Column('f_value', sa.Float(), nullable=True),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'last_updates',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('update_type', sa.String(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'crontabs',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('cron_name', sa.String(), nullable=False),
        sa.Column('status', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'user_activity_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('ip', sa.String(), nullable=True),
        sa.Column('action', sa.String(), nullable=True),
        sa.Column('user', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'market_groups',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('market_groups.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'blueprints',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column('produced_type_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('nb_runs', sa.Integer(), nullable=False),
        sa.Column('prod_qtt', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # --- universe hierarchy ---
    op.create_table(
        'universe_regions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('orders_pages_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('market_items', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('market_items_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('download_process_id', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'universe_constellations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('universe_region_id', sa.Integer(), sa.ForeignKey('universe_regions.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'universe_systems',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('trade_hub', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_inner', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('star_id', sa.Integer(), nullable=True),
        sa.Column('security_class', sa.String(), nullable=True),
        sa.Column('security_status', sa.Float(), nullable=False),
        sa.Column('kill_stats_current_month', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('kill_stats_last_month', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('universe_constellation_id', sa.Integer(), sa.ForeignKey('universe_constellations.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'universe_stations',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('services', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('office_rental_cost', sa.Float(), nullable=False),
        sa.Column('security_status', sa.Float(), nullable=True),
        sa.Column('jita_distance', sa.Integer(), nullable=True),
        sa.Column('industry_costs_indices', sa.Text(), nullable=True),
        sa.Column('universe_system_id', sa.Integer(), sa.ForeignKey('universe_systems.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'universe_structures',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('type_id', sa.Integer(), nullable=True),
        sa.Column('universe_system_id', sa.Integer(), sa.ForeignKey('universe_systems.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # --- eve_items (depends on market_groups + blueprints) ---
    op.create_table(
        'eve_items',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('market_group_id', sa.Integer(), sa.ForeignKey('market_groups.id'), nullable=True),
        sa.Column('blueprint_id', sa.Integer(), sa.ForeignKey('blueprints.id'), nullable=True),
        sa.Column('volume', sa.Float(), nullable=True),
        sa.Column('production_level', sa.Integer(), nullable=True),
        sa.Column('base_item', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('cpp_market_adjusted_price', sa.Float(), nullable=True),
        sa.Column('cpp_market_average_price', sa.Float(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('market_group_path', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('mass', sa.Float(), nullable=True),
        sa.Column('packaged_volume', sa.Float(), nullable=True),
        sa.Column('weekly_avg_price', sa.Float(), nullable=True),
        sa.Column('faction', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('slug', sa.String(), nullable=True, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # --- users (depends on universe_stations) ---
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('uid', sa.String(), nullable=True),
        sa.Column('expires_on', sa.DateTime(), nullable=True),
        sa.Column('token', sa.String(), nullable=True),
        sa.Column('renew_token', sa.String(), nullable=True),
        sa.Column('admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('locked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('batch_cap', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('batch_cap_multiplier', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('vol_month_pcent', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('min_pcent_for_advice', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('min_amount_for_advice', sa.Integer(), nullable=False, server_default='5000000'),
        sa.Column('remove_occuped_places', sa.Boolean(), nullable=True),
        sa.Column('watch_my_prices', sa.Boolean(), nullable=True),
        sa.Column('last_changes_in_choices', sa.DateTime(), nullable=True),
        sa.Column('download_assets_running', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_assets_download', sa.DateTime(), nullable=True),
        sa.Column('download_orders_running', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_orders_download', sa.DateTime(), nullable=True),
        sa.Column('download_blueprints_running', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_blueprints_download', sa.DateTime(), nullable=True),
        sa.Column('selected_assets_station_id', sa.BigInteger(), sa.ForeignKey('universe_stations.id'), nullable=True),
        sa.Column('current_location_station_id', sa.BigInteger(), sa.ForeignKey('universe_stations.id'), nullable=True),
        sa.Column('last_duplication_receiver_id', sa.Integer(), nullable=True),
        sa.Column('sales_orders_show_margin_min', sa.Integer(), nullable=True),
        sa.Column('initialization_finalized', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # --- association tables ---
    op.create_table(
        'eve_items_users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('eve_item_id', sa.BigInteger(), sa.ForeignKey('eve_items.id'), nullable=True),
    )

    op.create_table(
        'trade_hubs_users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('universe_system_id', sa.Integer(), sa.ForeignKey('universe_systems.id'), nullable=True),
    )

    op.create_table(
        'user_blueprints',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('blueprint_id', sa.Integer(), sa.ForeignKey('blueprints.id'), nullable=True),
    )

    # --- child tables ---
    op.create_table(
        'blueprint_materials',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('blueprint_id', sa.Integer(), sa.ForeignKey('blueprints.id'), nullable=False),
        sa.Column('required_qtt', sa.Integer(), nullable=False),
        sa.Column('eve_item_id', sa.BigInteger(), sa.ForeignKey('eve_items.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_blueprint_materials_blueprint_id', 'blueprint_materials', ['blueprint_id'])
    op.create_index('ix_blueprint_materials_eve_item_id', 'blueprint_materials', ['eve_item_id'])

    op.create_table(
        'blueprint_modifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('blueprint_id', sa.Integer(), sa.ForeignKey('blueprints.id'), nullable=False),
        sa.Column('percent_modification_value', sa.Float(), nullable=False),
        sa.Column('touched', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'prices_mins',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('eve_item_id', sa.BigInteger(), sa.ForeignKey('eve_items.id'), nullable=True),
        sa.Column('universe_system_id', sa.Integer(), sa.ForeignKey('universe_systems.id'), nullable=True),
        sa.Column('min_price', sa.Float(), nullable=True),
        sa.Column('volume', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('universe_system_id', 'eve_item_id', name='uq_prices_mins_hub_item'),
    )

    op.create_table(
        'prices_advices',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('eve_item_id', sa.BigInteger(), sa.ForeignKey('eve_items.id'), nullable=False),
        sa.Column('universe_system_id', sa.Integer(), sa.ForeignKey('universe_systems.id'), nullable=False),
        sa.Column('vol_month', sa.BigInteger(), nullable=True),
        sa.Column('avg_price_month', sa.Float(), nullable=True),
        sa.Column('immediate_montly_pcent', sa.Float(), nullable=True),
        sa.Column('margin_percent', sa.Float(), nullable=True),
        sa.Column('avg_price_week', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('eve_item_id', 'universe_system_id', name='uq_prices_advices_item_hub'),
    )

    op.create_table(
        'public_trade_orders',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('universe_system_id', sa.Integer(), sa.ForeignKey('universe_systems.id'), nullable=False),
        sa.Column('eve_item_id', sa.BigInteger(), sa.ForeignKey('eve_items.id'), nullable=False),
        sa.Column('order_id', sa.BigInteger(), nullable=False, unique=True),
        sa.Column('is_buy_order', sa.Boolean(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('range', sa.String(), nullable=False),
        sa.Column('volume_remain', sa.BigInteger(), nullable=False),
        sa.Column('volume_total', sa.BigInteger(), nullable=False),
        sa.Column('min_volume', sa.BigInteger(), nullable=False),
        sa.Column('location_id', sa.BigInteger(), nullable=True),
        sa.Column('touched', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index(
        'idx_public_trade_orders_analytics_lookup',
        'public_trade_orders',
        ['universe_system_id', 'eve_item_id', 'is_buy_order', 'price', 'volume_remain'],
    )

    op.create_table(
        'buy_orders_analytics',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('universe_system_id', sa.Integer(), sa.ForeignKey('universe_systems.id'), nullable=False),
        sa.Column('eve_item_id', sa.BigInteger(), sa.ForeignKey('eve_items.id'), nullable=False),
        sa.Column('approx_max_price', sa.Float(), nullable=True),
        sa.Column('over_approx_max_price_volume', sa.BigInteger(), nullable=True),
        sa.Column('single_unit_cost', sa.Float(), nullable=True),
        sa.Column('single_unit_margin', sa.Float(), nullable=True),
        sa.Column('estimated_volume_margin', sa.Float(), nullable=True),
        sa.Column('per_job_margin', sa.Float(), nullable=True),
        sa.Column('per_job_run_margin', sa.Float(), nullable=True),
        sa.Column('final_margin', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('universe_system_id', 'eve_item_id', name='uq_buy_orders_analytics_hub_item'),
    )

    op.create_table(
        'sales_finals',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('day', sa.Date(), nullable=False),
        sa.Column('universe_system_id', sa.Integer(), sa.ForeignKey('universe_systems.id'), nullable=False),
        sa.Column('eve_item_id', sa.BigInteger(), sa.ForeignKey('eve_items.id'), nullable=False),
        sa.Column('volume', sa.BigInteger(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('order_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'production_lists',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('universe_system_id', sa.Integer(), sa.ForeignKey('universe_systems.id'), nullable=False),
        sa.Column('eve_item_id', sa.BigInteger(), sa.ForeignKey('eve_items.id'), nullable=False),
        sa.Column('runs_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'user_sale_orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('eve_item_id', sa.BigInteger(), sa.ForeignKey('eve_items.id'), nullable=False),
        sa.Column('universe_system_id', sa.Integer(), sa.ForeignKey('universe_systems.id'), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'eve_items_saved_lists',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('saved_ids', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'eve_market_histories_groups',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('eve_item_id', sa.BigInteger(), sa.ForeignKey('eve_items.id'), nullable=False),
        sa.Column('volume', sa.BigInteger(), nullable=False),
        sa.Column('highest', sa.Float(), nullable=True),
        sa.Column('lowest', sa.Float(), nullable=True),
        sa.Column('average', sa.Float(), nullable=True),
        sa.Column('universe_region_id', sa.Integer(), sa.ForeignKey('universe_regions.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'weekly_price_details',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('eve_item_id', sa.BigInteger(), sa.ForeignKey('eve_items.id'), nullable=False),
        sa.Column('universe_system_id', sa.Integer(), sa.ForeignKey('universe_systems.id'), nullable=False),
        sa.Column('day', sa.Date(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('weighted_avg_price', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('eve_item_id', 'universe_system_id', 'day', name='uq_weekly_price_details_item_hub_day'),
    )

    op.create_table(
        'bpc_assets',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('universe_station_id', sa.BigInteger(), sa.ForeignKey('universe_stations.id'), nullable=True),
        sa.Column('universe_structure_id', sa.BigInteger(), sa.ForeignKey('universe_structures.id'), nullable=True),
        sa.Column('quantity', sa.BigInteger(), nullable=False),
        sa.Column('touched', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('eve_item_id', sa.BigInteger(), sa.ForeignKey('eve_items.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'bpc_assets_stations',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('universe_station_id', sa.BigInteger(), sa.ForeignKey('universe_stations.id'), nullable=False),
        sa.Column('touched', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'user_to_user_duplication_requests',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('sender_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('receiver_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('duplication_type', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # --- SQL views ---
    conn = op.get_bind()

    conn.execute(sa.text("""
        CREATE VIEW buy_orders_analytics_results AS
        SELECT boa.id,
          u.id AS user_id,
          boa.universe_system_id,
          boa.eve_item_id,
          (us.name || ' (' || ur.name || ')') AS trade_hub_name,
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
        JOIN universe_systems us ON boa.universe_system_id = us.id
        JOIN universe_constellations uc ON us.universe_constellation_id = uc.id
        JOIN universe_regions ur ON uc.universe_region_id = ur.id
        JOIN trade_hubs_users thu ON boa.universe_system_id = thu.universe_system_id
        JOIN eve_items_users eiu ON boa.eve_item_id = eiu.eve_item_id
        JOIN users u ON thu.user_id = u.id AND eiu.user_id = u.id
        JOIN blueprints bp ON ei.blueprint_id = bp.id
        WHERE boa.over_approx_max_price_volume > 0
    """))

    conn.execute(sa.text("""
        CREATE VIEW price_advices_min_prices AS
        SELECT pa.id,
          ei.id AS eve_item_id,
          us.id AS trade_hub_id,
          (us.name || ' (' || ur.name || ')') AS trade_hub_name,
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
        JOIN universe_systems us ON pa.universe_system_id = us.id
        JOIN universe_constellations uc ON us.universe_constellation_id = uc.id
        JOIN universe_regions ur ON uc.universe_region_id = ur.id
        LEFT JOIN prices_mins pm ON pm.universe_system_id = pa.universe_system_id
          AND pa.eve_item_id = pm.eve_item_id
    """))

    conn.execute(sa.text("""
        CREATE VIEW price_advice_margin_comps AS
        SELECT pa.id,
          pu.id AS user_id,
          ei.id AS item_id,
          us.id AS trade_hub_id,
          ur.name AS region_name,
          us.name AS trade_hub_name,
          ei.name AS item_name,
          ei.cost AS single_unit_cost,
          pm.min_price,
          ei.weekly_avg_price AS price_avg_week,
          pa.vol_month,
          (bp.nb_runs * bp.prod_qtt) AS full_batch_size,
          pa.immediate_montly_pcent AS daily_monthly_pcent,
          pa.margin_percent,
          CASE
            WHEN pu.batch_cap THEN LEAST(
              CAST(bp.nb_runs * bp.prod_qtt * pu.batch_cap_multiplier AS REAL),
              CAST(floor(pa.vol_month * pu.vol_month_pcent * 0.01) AS REAL))
            ELSE CAST(floor(pa.vol_month * pu.vol_month_pcent * 0.01) AS REAL)
          END AS batch_size_formula,
          pu.min_amount_for_advice,
          pu.min_pcent_for_advice,
          (pm.min_price * CASE
            WHEN pu.batch_cap THEN LEAST(
              CAST(bp.nb_runs * bp.prod_qtt * pu.batch_cap_multiplier AS REAL),
              CAST(floor(pa.vol_month * pu.vol_month_pcent * 0.01) AS REAL))
            ELSE CAST(floor(pa.vol_month * pu.vol_month_pcent * 0.01) AS REAL)
          END
          - ei.cost * CASE
            WHEN pu.batch_cap THEN LEAST(
              CAST(bp.nb_runs * bp.prod_qtt * pu.batch_cap_multiplier AS REAL),
              CAST(floor(pa.vol_month * pu.vol_month_pcent * 0.01) AS REAL))
            ELSE CAST(floor(pa.vol_month * pu.vol_month_pcent * 0.01) AS REAL)
          END) AS margin_comp_immediate,
          (ei.weekly_avg_price * CASE
            WHEN pu.batch_cap THEN LEAST(
              CAST(bp.nb_runs * bp.prod_qtt * pu.batch_cap_multiplier AS REAL),
              CAST(floor(pa.vol_month * pu.vol_month_pcent * 0.01) AS REAL))
            ELSE CAST(floor(pa.vol_month * pu.vol_month_pcent * 0.01) AS REAL)
          END
          - ei.cost * CASE
            WHEN pu.batch_cap THEN LEAST(
              CAST(bp.nb_runs * bp.prod_qtt * pu.batch_cap_multiplier AS REAL),
              CAST(floor(pa.vol_month * pu.vol_month_pcent * 0.01) AS REAL))
            ELSE CAST(floor(pa.vol_month * pu.vol_month_pcent * 0.01) AS REAL)
          END) AS margin_comp_weekly
        FROM prices_advices pa
        JOIN eve_items ei ON pa.eve_item_id = ei.id
        JOIN blueprints bp ON ei.blueprint_id = bp.id
        JOIN universe_systems us ON pa.universe_system_id = us.id
        JOIN universe_constellations uc ON us.universe_constellation_id = uc.id
        JOIN universe_regions ur ON uc.universe_region_id = ur.id
        JOIN trade_hubs_users thu ON thu.universe_system_id = pa.universe_system_id
        JOIN eve_items_users eiu ON eiu.eve_item_id = pa.eve_item_id
        JOIN users pu ON thu.user_id = pu.id AND eiu.user_id = pu.id
        JOIN prices_mins pm ON pm.universe_system_id = pa.universe_system_id
          AND pa.eve_item_id = pm.eve_item_id
        WHERE pa.vol_month IS NOT NULL
    """))

    conn.execute(sa.text("""
        CREATE VIEW components_to_buys AS
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
        JOIN eve_items bpm_mat_ei ON bm.eve_item_id = bpm_mat_ei.id
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
    """))

    conn.execute(sa.text("""
        CREATE VIEW user_sale_order_details AS
        SELECT uso.id,
          uso.user_id,
          (us.name || ' (' || ur.name || ')') AS trade_hub_name,
          ei.name AS eve_item_name,
          uso.price AS my_price,
          pm.min_price,
          ei.cost,
          b.prod_qtt,
          (pm.min_price / ei.cost - 1.0) AS min_price_margin_pcent,
          (pm.min_price - uso.price) AS price_delta,
          uso.eve_item_id,
          uso.universe_system_id AS trade_hub_id,
          us.id AS eve_system_id
        FROM user_sale_orders uso
        JOIN eve_items ei ON ei.id = uso.eve_item_id
        JOIN blueprints b ON ei.blueprint_id = b.id
        JOIN universe_systems us ON uso.universe_system_id = us.id
        JOIN universe_constellations uc ON us.universe_constellation_id = uc.id
        JOIN universe_regions ur ON uc.universe_region_id = ur.id
        LEFT JOIN prices_mins pm ON pm.eve_item_id = uso.eve_item_id
          AND pm.universe_system_id = uso.universe_system_id
    """))

    # --- materialized views ---
    conn.execute(sa.text("""
        CREATE MATERIALIZED VIEW jita_prices AS
        WITH
        jita AS (
            SELECT id FROM universe_systems WHERE id = 30000142 AND trade_hub = TRUE
        ),
        sell AS (
            SELECT ei.id, pto.price, pto.volume_remain,
                SUM(pto.volume_remain) OVER (
                    PARTITION BY pto.eve_item_id ORDER BY pto.price ASC
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS cum_vol,
                SUM(pto.volume_remain) OVER (PARTITION BY pto.eve_item_id) AS total_vol
            FROM public_trade_orders pto
            JOIN eve_items ei ON pto.eve_item_id = ei.id
            WHERE pto.is_buy_order = false AND pto.universe_system_id = (SELECT id FROM jita)
        ),
        sell_p10 AS (
            SELECT id, MIN(price) AS min_sell_price
            FROM sell WHERE cum_vol >= total_vol * 0.10
            GROUP BY id
        ),
        buy AS (
            SELECT ei.id, pto.price, pto.volume_remain,
                SUM(pto.volume_remain) OVER (
                    PARTITION BY pto.eve_item_id ORDER BY pto.price ASC
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS cum_vol,
                SUM(pto.volume_remain) OVER (PARTITION BY pto.eve_item_id) AS total_vol
            FROM public_trade_orders pto
            JOIN eve_items ei ON pto.eve_item_id = ei.id
            WHERE pto.is_buy_order = true AND pto.universe_system_id = (SELECT id FROM jita)
        ),
        buy_p90 AS (
            SELECT id, MIN(price) * 0.9 AS max_buy_price
            FROM buy WHERE cum_vol >= total_vol * 0.90
            GROUP BY id
        ),
        all_items AS (
            SELECT id FROM sell_p10
            UNION
            SELECT id FROM buy_p90
        )
        SELECT a.id, s.min_sell_price, b.max_buy_price,
            s.min_sell_price - b.max_buy_price AS spread
        FROM all_items a
        LEFT JOIN sell_p10 s ON a.id = s.id
        LEFT JOIN buy_p90  b ON a.id = b.id
        WITH NO DATA
    """))

    conn.execute(sa.text("""
        CREATE MATERIALIZED VIEW jita_manufacturing_margins AS
        WITH mat_costs AS (
            SELECT
                b.produced_type_id,
                b.prod_qtt,
                SUM(bm.required_qtt::bigint * jp.min_sell_price) AS manufacturing_cost
            FROM blueprints b
            JOIN blueprint_materials bm ON bm.blueprint_id = b.id
            JOIN eve_items ei_mat ON ei_mat.id = bm.eve_item_id
            JOIN jita_prices jp ON jp.id = ei_mat.id
            GROUP BY b.produced_type_id, b.prod_qtt
        )
        SELECT
            mc.produced_type_id                                       AS id,
            ei.id                                                         AS eve_item_id,
            mc.manufacturing_cost,
            mc.manufacturing_cost * 0.10                                  AS manufacturing_tax,
            mc.prod_qtt::bigint * jp_prod.min_sell_price                  AS estimated_selling_price,
            mc.prod_qtt::bigint * jp_prod.min_sell_price * 0.05           AS selling_tax,
            (mc.prod_qtt::bigint * jp_prod.min_sell_price)
                - (mc.prod_qtt::bigint * jp_prod.min_sell_price * 0.05)
                - mc.manufacturing_cost
                - (mc.manufacturing_cost * 0.10)                          AS benefit
        FROM mat_costs mc
        JOIN eve_items ei        ON ei.id        = mc.produced_type_id
        JOIN jita_prices jp_prod ON jp_prod.id   = mc.produced_type_id
        WITH NO DATA
    """))
    conn.execute(sa.text('CREATE UNIQUE INDEX ON jita_manufacturing_margins (id)'))


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
