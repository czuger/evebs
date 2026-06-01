"""Drop trade_hubs table: migrate trade_hub_id → universe_system_id, add inner to universe_systems.

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-05-31
"""
from __future__ import annotations
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, None] = 'd0e1f2a3b4c5'
branch_labels = None
depends_on = None

# Tables that need trade_hub_id renamed + widened to BigInteger
_TABLES_WIDEN = ['prices_mins', 'prices_advices', 'production_lists', 'user_sale_orders']
# Tables already BigInteger, just rename
_TABLES_RENAME = ['buy_orders_analytics', 'public_trade_orders', 'sales_finals', 'weekly_price_details']

_ALL_DATA_TABLES = _TABLES_WIDEN + _TABLES_RENAME
_ASSOC_TABLE = 'trade_hubs_users'

# PostgreSQL auto-generated FK constraint names
_FK_NAMES = {
    'prices_mins':          'prices_mins_trade_hub_id_fkey',
    'prices_advices':       'prices_advices_trade_hub_id_fkey',
    'production_lists':     'production_lists_trade_hub_id_fkey',
    'user_sale_orders':     'user_sale_orders_trade_hub_id_fkey',
    'buy_orders_analytics': 'buy_orders_analytics_trade_hub_id_fkey',
    'public_trade_orders':  'public_trade_orders_trade_hub_id_fkey',
    'sales_finals':         'sales_finals_trade_hub_id_fkey',
    'weekly_price_details': 'weekly_price_details_trade_hub_id_fkey',
    'trade_hubs_users':     'trade_hubs_users_trade_hub_id_fkey',
}

_OLD_MAT_VIEWS = [
    'jita_manufacturing_margins',  # depends on jita_prices, must drop first
    'jita_prices',
]

_OLD_VIEWS = [
    'buy_orders_analytics_results',
    'price_advices_min_prices',
    'user_sale_order_details',
    'price_advice_margin_comps',
]

_NEW_VIEWS = [
    ('buy_orders_analytics_results', """
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
    """),
    ('price_advices_min_prices', """
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
    """),
    ('user_sale_order_details', """
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
          ei.cpp_eve_item_id,
          us.cpp_system_id AS eve_system_id
        FROM user_sale_orders uso
        JOIN eve_items ei ON ei.id = uso.eve_item_id
        JOIN blueprints b ON ei.blueprint_id = b.id
        JOIN universe_systems us ON uso.universe_system_id = us.id
        JOIN universe_constellations uc ON us.universe_constellation_id = uc.id
        JOIN universe_regions ur ON uc.universe_region_id = ur.id
        LEFT JOIN prices_mins pm ON pm.eve_item_id = uso.eve_item_id
          AND pm.universe_system_id = uso.universe_system_id
    """),
    ('price_advice_margin_comps', """
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
    """),
]


def upgrade() -> None:
    conn = op.get_bind()

    # Drop materialized views (dependency order: jita_manufacturing_margins → jita_prices → trade_hubs)
    for view_name in _OLD_MAT_VIEWS:
        op.execute(f'DROP MATERIALIZED VIEW IF EXISTS {view_name}')

    # Drop regular views that reference trade_hubs
    for view_name in _OLD_VIEWS:
        op.execute(f'DROP VIEW IF EXISTS {view_name}')

    # Add is_inner column to universe_systems
    op.add_column('universe_systems', sa.Column('is_inner', sa.Boolean(), nullable=False, server_default='false'))

    # Populate is_inner from trade_hubs data (trade_hubs.inner is a reserved word, must be quoted)
    conn.execute(sa.text("""
        UPDATE universe_systems
        SET is_inner = th."inner"
        FROM trade_hubs th
        WHERE universe_systems.cpp_system_id = th.eve_system_id
    """))

    # Drop all FK constraints
    for table, fk_name in _FK_NAMES.items():
        op.drop_constraint(fk_name, table, type_='foreignkey')

    # Remap trade_hub_id values: old trade_hubs.id → universe_systems.id
    for table in _ALL_DATA_TABLES + [_ASSOC_TABLE]:
        conn.execute(sa.text(f"""
            UPDATE {table}
            SET trade_hub_id = us.id
            FROM trade_hubs th
            JOIN universe_systems us ON us.cpp_system_id = th.eve_system_id
            WHERE {table}.trade_hub_id = th.id
        """))

    # Widen Integer → BigInteger and rename column for tables that need widening
    for table in _TABLES_WIDEN:
        op.alter_column(table, 'trade_hub_id', type_=sa.BigInteger(), existing_type=sa.Integer())

    # Widen trade_hubs_users.trade_hub_id
    op.alter_column(_ASSOC_TABLE, 'trade_hub_id', type_=sa.BigInteger(), existing_type=sa.Integer())

    # Rename trade_hub_id → universe_system_id in all tables
    for table in _ALL_DATA_TABLES + [_ASSOC_TABLE]:
        op.alter_column(table, 'trade_hub_id', new_column_name='universe_system_id')

    # Re-add FK constraints → universe_systems
    for table in _ALL_DATA_TABLES + [_ASSOC_TABLE]:
        op.create_foreign_key(
            f'{table}_universe_system_id_fkey',
            table, 'universe_systems',
            ['universe_system_id'], ['id'],
        )

    # Partial index for trade hub system lookup
    op.execute(
        'CREATE INDEX idx_universe_systems_trade_hub ON universe_systems (id) WHERE trade_hub = TRUE'
    )

    # Drop the trade_hubs table (and its FK to regions)
    op.drop_constraint('trade_hubs_region_id_fkey', 'trade_hubs', type_='foreignkey')
    op.drop_table('trade_hubs')

    # Remove server_default (column managed by ORM)
    op.alter_column('universe_systems', 'is_inner', server_default=None)

    # Recreate views with universe_systems joins
    for view_name, select_sql in _NEW_VIEWS:
        op.execute(f'CREATE VIEW {view_name} AS {select_sql}')

    # Recreate jita_prices using universe_systems instead of trade_hubs
    op.execute("""
        CREATE MATERIALIZED VIEW jita_prices AS
        WITH
        jita AS (
            SELECT id FROM universe_systems WHERE cpp_system_id = 30000142 AND trade_hub = TRUE
        ),
        sell AS (
            SELECT ei.cpp_eve_item_id, pto.price, pto.volume_remain,
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
            SELECT cpp_eve_item_id, MIN(price) AS min_sell_price
            FROM sell WHERE cum_vol >= total_vol * 0.10
            GROUP BY cpp_eve_item_id
        ),
        buy AS (
            SELECT ei.cpp_eve_item_id, pto.price, pto.volume_remain,
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
            SELECT cpp_eve_item_id, MIN(price) * 0.9 AS max_buy_price
            FROM buy WHERE cum_vol >= total_vol * 0.90
            GROUP BY cpp_eve_item_id
        ),
        all_items AS (
            SELECT cpp_eve_item_id FROM sell_p10
            UNION
            SELECT cpp_eve_item_id FROM buy_p90
        )
        SELECT a.cpp_eve_item_id, s.min_sell_price, b.max_buy_price,
            s.min_sell_price - b.max_buy_price AS spread
        FROM all_items a
        LEFT JOIN sell_p10 s ON a.cpp_eve_item_id = s.cpp_eve_item_id
        LEFT JOIN buy_p90  b ON a.cpp_eve_item_id = b.cpp_eve_item_id
        WITH NO DATA
    """)

    # Recreate jita_manufacturing_margins (unchanged — only references jita_prices)
    op.execute("""
        CREATE MATERIALIZED VIEW jita_manufacturing_margins AS
        WITH mat_costs AS (
            SELECT
                b.produced_cpp_type_id,
                b.prod_qtt,
                SUM(bm.required_qtt::bigint * jp.min_sell_price) AS manufacturing_cost
            FROM blueprints b
            JOIN blueprint_materials bm ON bm.blueprint_id = b.id
            JOIN eve_items ei_mat ON ei_mat.id = bm.eve_item_id
            JOIN jita_prices jp ON jp.cpp_eve_item_id = ei_mat.cpp_eve_item_id
            GROUP BY b.produced_cpp_type_id, b.prod_qtt
        )
        SELECT
            mc.produced_cpp_type_id                                      AS cpp_eve_item_id,
            ei.id                                                        AS eve_item_id,
            mc.manufacturing_cost,
            mc.manufacturing_cost * 0.10                                 AS manufacturing_tax,
            mc.prod_qtt::bigint * jp_prod.min_sell_price                  AS estimated_selling_price,
            mc.prod_qtt::bigint * jp_prod.min_sell_price * 0.05           AS selling_tax,
            (mc.prod_qtt::bigint * jp_prod.min_sell_price)
                - (mc.prod_qtt::bigint * jp_prod.min_sell_price * 0.05)
                - mc.manufacturing_cost
                - (mc.manufacturing_cost * 0.10)                         AS benefit
        FROM mat_costs mc
        JOIN eve_items ei        ON ei.cpp_eve_item_id   = mc.produced_cpp_type_id
        JOIN jita_prices jp_prod ON jp_prod.cpp_eve_item_id = mc.produced_cpp_type_id
        WITH NO DATA
    """)


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
