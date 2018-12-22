SELECT
  pa.id,
  ei.id eve_item_id,
  tu.id trade_hub_id,
  tu.name || ' (' || re.name || ')' trade_hub_name,
  ei.name item_name,
  ei.cost,
  min_price,
  avg_price_week,
  avg_price_month,
  vol_month,
  nb_runs * bp.prod_qtt full_batch_size,
  immediate_montly_pcent,
  margin_percent,
  CASE WHEN ei.cost = '+infinity' THEN '+infinity'
    ELSE ( avg_price_month / ei.cost ) - 1
  END avg_monthly_margin_percent
FROM prices_advices pa
  JOIN eve_items ei ON pa.eve_item_id = ei.id
  JOIN blueprints bp ON ei.blueprint_id = bp.id
  JOIN trade_hubs tu ON pa.trade_hub_id = tu.id
  JOIN regions re ON re.id = tu.region_id
  LEFT JOIN prices_mins pm ON pm.trade_hub_id = pa.trade_hub_id AND pa.eve_item_id = pm.eve_item_id