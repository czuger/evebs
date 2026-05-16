SELECT boa.id,
  u.id user_id,
  boa.trade_hub_id,
  boa.eve_item_id,
  tu.name || ' (' || r.name || ')' trade_hub_name,
  ei.name eve_item_name,
  over_approx_max_price_volume,
  approx_max_price,
  single_unit_cost,
  single_unit_margin,
  1 - single_unit_cost / approx_max_price margin_pcent,
  over_approx_max_price_volume * single_unit_margin full_margin,

  bp.nb_runs * bp.prod_qtt * u.batch_cap_multiplier batch_cap,
  LEAST( over_approx_max_price_volume, bp.nb_runs * bp.prod_qtt * u.batch_cap_multiplier ) capped_volume,
  LEAST( over_approx_max_price_volume, bp.nb_runs * bp.prod_qtt * u.batch_cap_multiplier ) * single_unit_margin capped_margin
FROM buy_orders_analytics boa
  JOIN eve_items ei ON ei.id = boa.eve_item_id
  JOIN trade_hubs tu ON boa.trade_hub_id = tu.id
  JOIN trade_hubs_users thu ON boa.trade_hub_id = thu.trade_hub_id
  JOIN eve_items_users eiu ON boa.eve_item_id = eiu.eve_item_id
  JOIN users u ON thu.user_id = u.id AND eiu.user_id = u.id
  JOIN regions r ON tu.region_id = r.id
  JOIN blueprints bp ON ei.blueprint_id = bp.id
  AND over_approx_max_price_volume > 0;