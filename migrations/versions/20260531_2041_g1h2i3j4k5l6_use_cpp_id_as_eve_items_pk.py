"""Use cpp_eve_item_id as eve_items primary key — drop auto-increment id.

Revision ID: g1h2i3j4k5l6
Revises: f6a7b8c9d0e1
Create Date: 2026-05-31
"""
from __future__ import annotations
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = 'g1h2i3j4k5l6'
down_revision: Union[str, None] = 'e1f2a3b4c5d6'
branch_labels = None
depends_on = None

_CHILD_TABLES = [
    'blueprint_materials',
    'eve_market_histories_groups',
    'prices_mins',
    'prices_advices',
    'user_sale_orders',
    'sales_finals',
    'bpc_assets',
    'weekly_price_details',
    'buy_orders_analytics',
    'public_trade_orders',
    'production_lists',
    'eve_items_users',
]

# Tables whose eve_item_id column is still Integer and needs widening to BigInteger
_WIDEN_TABLES = [
    'prices_mins',
    'prices_advices',
    'user_sale_orders',
    'production_lists',
    'eve_items_users',
]

# Views that depend on columns being widened in step 5 — must be dropped before
# and recreated after (SQL unchanged from the e1f2a3b4c5d6 migration).
_APP_VIEWS_TO_CYCLE = [
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
    ('components_to_buys', """
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
    """),
]

_USER_SALE_ORDER_DETAILS_SQL = """
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
      ei.id AS cpp_eve_item_id,
      us.cpp_system_id AS eve_system_id
    FROM user_sale_orders uso
    JOIN eve_items ei ON ei.id = uso.eve_item_id
    JOIN blueprints b ON ei.blueprint_id = b.id
    JOIN universe_systems us ON uso.universe_system_id = us.id
    JOIN universe_constellations uc ON us.universe_constellation_id = uc.id
    JOIN universe_regions ur ON uc.universe_region_id = ur.id
    LEFT JOIN prices_mins pm ON pm.eve_item_id = uso.eve_item_id
      AND pm.universe_system_id = uso.universe_system_id
"""

_JITA_PRICES_MV_SQL = """
CREATE MATERIALIZED VIEW jita_prices AS
WITH
jita AS (
    SELECT id FROM universe_systems WHERE cpp_system_id = 30000142 AND trade_hub = TRUE
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
"""

_JITA_MANUFACTURING_MARGINS_MV_SQL = """
CREATE MATERIALIZED VIEW jita_manufacturing_margins AS
WITH mat_costs AS (
    SELECT
        b.produced_cpp_type_id,
        b.prod_qtt,
        SUM(bm.required_qtt::bigint * jp.min_sell_price) AS manufacturing_cost
    FROM blueprints b
    JOIN blueprint_materials bm ON bm.blueprint_id = b.id
    JOIN eve_items ei_mat ON ei_mat.id = bm.eve_item_id
    JOIN jita_prices jp ON jp.id = ei_mat.id
    GROUP BY b.produced_cpp_type_id, b.prod_qtt
)
SELECT
    mc.produced_cpp_type_id                                       AS id,
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
JOIN eve_items ei        ON ei.id        = mc.produced_cpp_type_id
JOIN jita_prices jp_prod ON jp_prod.id   = mc.produced_cpp_type_id
WITH NO DATA
"""


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Drop materialized views (depend on eve_items.cpp_eve_item_id)
    conn.execute(sa.text('DROP MATERIALIZED VIEW IF EXISTS jita_manufacturing_margins'))
    conn.execute(sa.text('DROP MATERIALIZED VIEW IF EXISTS jita_prices'))

    # 2. Drop regular views — user_sale_order_details references cpp_eve_item_id (renamed in step 6);
    #    the others block the column widening in step 5 because PostgreSQL forbids altering a
    #    column type while any view rule depends on it.
    conn.execute(sa.text('DROP VIEW IF EXISTS user_sale_order_details'))
    for view_name, _ in _APP_VIEWS_TO_CYCLE:
        conn.execute(sa.text(f'DROP VIEW IF EXISTS {view_name}'))

    # 3. Drop FK constraints from all child tables
    for table in _CHILD_TABLES:
        conn.execute(sa.text(
            f'ALTER TABLE {table} DROP CONSTRAINT {table}_eve_item_id_fkey'
        ))

    # 4a. Drop unique constraints that include eve_item_id — PostgreSQL checks
    #     IMMEDIATE unique constraints per-row during UPDATE, which would falsely
    #     fail when two rows swap values.  We recreate them in step 7b.
    _UNIQUE_CONSTRAINTS = [
        ('prices_mins',          'uq_prices_mins_hub_item'),
        ('buy_orders_analytics', 'uq_buy_orders_analytics_hub_item'),
        ('prices_advices',       'uq_prices_advices_item_hub'),
        ('weekly_price_details', 'uq_weekly_price_details_item_hub_day'),
    ]
    for table, cname in _UNIQUE_CONSTRAINTS:
        conn.execute(sa.text(f'ALTER TABLE {table} DROP CONSTRAINT {cname}'))

    # 4b. Remap FK values: old auto-increment id → cpp_eve_item_id
    for table in _CHILD_TABLES:
        conn.execute(sa.text(f"""
            UPDATE {table}
            SET eve_item_id = e.cpp_eve_item_id
            FROM eve_items e
            WHERE {table}.eve_item_id = e.id
        """))

    # 5. Widen Integer → BigInteger on child tables that still have Integer
    for table in _WIDEN_TABLES:
        op.alter_column(table, 'eve_item_id', type_=sa.BigInteger(), existing_type=sa.Integer())

    # 6. Restructure eve_items: drop auto-increment id, promote cpp_eve_item_id to PK
    conn.execute(sa.text('ALTER TABLE eve_items DROP CONSTRAINT eve_items_pkey'))
    conn.execute(sa.text('ALTER TABLE eve_items DROP COLUMN id'))
    conn.execute(sa.text('ALTER TABLE eve_items RENAME COLUMN cpp_eve_item_id TO id'))
    conn.execute(sa.text('ALTER TABLE eve_items ALTER COLUMN id TYPE BIGINT'))
    conn.execute(sa.text('ALTER TABLE eve_items ADD CONSTRAINT eve_items_pkey PRIMARY KEY (id)'))

    # 7a. Re-add FK constraints
    for table in _CHILD_TABLES:
        conn.execute(sa.text(
            f'ALTER TABLE {table} ADD CONSTRAINT {table}_eve_item_id_fkey '
            f'FOREIGN KEY (eve_item_id) REFERENCES eve_items(id)'
        ))

    # 7b. Recreate unique constraints dropped in step 4a
    conn.execute(sa.text(
        'ALTER TABLE prices_mins ADD CONSTRAINT uq_prices_mins_hub_item '
        'UNIQUE (universe_system_id, eve_item_id)'
    ))
    conn.execute(sa.text(
        'ALTER TABLE buy_orders_analytics ADD CONSTRAINT uq_buy_orders_analytics_hub_item '
        'UNIQUE (universe_system_id, eve_item_id)'
    ))
    conn.execute(sa.text(
        'ALTER TABLE prices_advices ADD CONSTRAINT uq_prices_advices_item_hub '
        'UNIQUE (eve_item_id, universe_system_id)'
    ))
    conn.execute(sa.text(
        'ALTER TABLE weekly_price_details ADD CONSTRAINT uq_weekly_price_details_item_hub_day '
        'UNIQUE (eve_item_id, universe_system_id, day)'
    ))

    # 8. Recreate views dropped in step 2.
    conn.execute(sa.text(
        f'CREATE VIEW user_sale_order_details AS {_USER_SALE_ORDER_DETAILS_SQL}'
    ))
    for view_name, select_sql in _APP_VIEWS_TO_CYCLE:
        conn.execute(sa.text(f'CREATE VIEW {view_name} AS {select_sql}'))

    # 9. Recreate jita_prices with id column (was cpp_eve_item_id)
    conn.execute(sa.text(_JITA_PRICES_MV_SQL))

    # 10. Recreate jita_manufacturing_margins with updated joins
    conn.execute(sa.text(_JITA_MANUFACTURING_MARGINS_MV_SQL))
    conn.execute(sa.text('CREATE UNIQUE INDEX ON jita_manufacturing_margins (id)'))


def downgrade() -> None:
    raise NotImplementedError('Downgrade not supported — restore from backup.')
