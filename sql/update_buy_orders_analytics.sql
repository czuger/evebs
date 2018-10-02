INSERT INTO buy_orders_analytics ( trade_hub_id, eve_item_id, approx_max_price, created_at, updated_at )
  SELECT trade_hub_id, eve_item_id, MAX( price ) * 0.9, now(), now()
  FROM public_trade_orders
    WHERE is_buy_order = TRUE
  GROUP BY trade_hub_id, eve_item_id
ON CONFLICT (trade_hub_id, eve_item_id)
  DO UPDATE SET
    approx_max_price = EXCLUDED.approx_max_price,
    updated_at = now();

UPDATE buy_orders_analytics boa SET over_approx_max_price_volume =
( SELECT SUM( volume_remain )
  FROM public_trade_orders bo
  WHERE bo.price >= boa.approx_max_price
        AND bo.trade_hub_id = boa.trade_hub_id
        AND bo.eve_item_id = boa.eve_item_id
    AND is_buy_order = TRUE
  GROUP BY trade_hub_id, eve_item_id );

-- DELETE FROM buy_orders_analytics WHERE over_approx_max_price_volume IS NULL;

UPDATE buy_orders_analytics boa SET ( single_unit_cost, single_unit_margin, estimated_volume_margin, per_job_margin,
                                      per_job_run_margin, final_margin ) =
( SELECT cost,
    boa.approx_max_price - cost,
    ( boa.approx_max_price - cost ) * over_approx_max_price_volume,
    ( boa.approx_max_price - cost ) * ( bp.prod_qtt * bp.nb_runs ),
    ( boa.approx_max_price - cost ) * bp.prod_qtt,
    LEAST(
    ( boa.approx_max_price - cost ) * over_approx_max_price_volume,
    ( boa.approx_max_price - cost ) * ( bp.prod_qtt * bp.nb_runs )
  )
  FROM prices_advices pa
    LEFT JOIN eve_items ei ON pa.eve_item_id = ei.id
    LEFT JOIN blueprints bp ON ei.blueprint_id = bp.id
  WHERE pa.trade_hub_id = boa.trade_hub_id
  AND pa.eve_item_id = boa.eve_item_id );