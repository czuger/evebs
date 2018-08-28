INSERT INTO buy_orders_analytics ( trade_hub_id, eve_item_id, approx_max_price, created_at, updated_at )
  SELECT trade_hub_id, eve_item_id, MAX( price ) * 0.9, now(), now()
  FROM buy_orders
  GROUP BY trade_hub_id, eve_item_id
ON CONFLICT (trade_hub_id, eve_item_id)
  DO UPDATE SET
    approx_max_price = EXCLUDED.approx_max_price,
    updated_at = now();

UPDATE buy_orders_analytics boa SET over_approx_max_price_volume =
( SELECT SUM( volume_remain )
  FROM buy_orders bo
  WHERE bo.price >= boa.approx_max_price
        AND bo.trade_hub_id = boa.trade_hub_id
        AND bo.eve_item_id = boa.eve_item_id
  GROUP BY trade_hub_id, eve_item_id );

UPDATE buy_orders_analytics boa SET ( single_unit_cost, single_unit_margin, estimated_volume_margin, per_job_margin,
                                      per_job_run_margin, final_margin ) =
( SELECT single_unit_cost,
    boa.approx_max_price - single_unit_cost,
    ( boa.approx_max_price - single_unit_cost ) * over_approx_max_price_volume,
    ( boa.approx_max_price - single_unit_cost ) * ( bp.prod_qtt * bp.nb_runs ),
    ( boa.approx_max_price - single_unit_cost ) * bp.prod_qtt,
    LEAST(
    ( boa.approx_max_price - single_unit_cost ) * over_approx_max_price_volume,
    ( boa.approx_max_price - single_unit_cost ) * ( bp.prod_qtt * bp.nb_runs )
  )
  FROM prices_advices pa
    LEFT JOIN eve_items ei ON pa.eve_item_id = ei.id
    LEFT JOIN blueprints bp ON ei.blueprint_id = bp.id
  WHERE pa.trade_hub_id = boa.trade_hub_id
  AND pa.eve_item_id = boa.eve_item_id );

-- Avant de faire fonctionner ça il faut rajouter une colonne prix à l'unité dans eve item
-- Il faudra également la suprimer de prices advices, il faut une source unique.