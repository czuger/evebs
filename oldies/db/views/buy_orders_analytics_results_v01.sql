SELECT boa.id, u.id user_id, boa.trade_hub_id, boa.eve_item_id, tu.name || ' (' || r.name || ')' trade_hub_name,
  ei.name eve_item_name, approx_max_price,
  single_unit_cost, single_unit_margin, final_margin,
  per_job_margin, CEIL( final_margin / per_job_margin ) job_count,
  per_job_run_margin, FLOOR( final_margin / per_job_run_margin ) runs,
  FLOOR( final_margin / per_job_run_margin ) * per_job_run_margin true_margin,
  estimated_volume_margin, over_approx_max_price_volume
FROM buy_orders_analytics boa
  JOIN eve_items ei ON ei.id = boa.eve_item_id
  JOIN trade_hubs tu ON boa.trade_hub_id = tu.id
  JOIN trade_hubs_users thu ON boa.trade_hub_id = thu.trade_hub_id
  JOIN eve_items_users eiu ON boa.eve_item_id = eiu.eve_item_id
  JOIN users u ON thu.user_id = u.id AND eiu.user_id = u.id
  JOIN regions r ON tu.region_id = r.id
WHERE final_margin > 0
ORDER BY final_margin DESC;