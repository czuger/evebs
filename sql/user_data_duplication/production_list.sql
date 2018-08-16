INSERT INTO production_lists( user_id, trade_hub_id, eve_item_id, created_at, updated_at, quantity_to_produce, runs_count )
  SELECT $1, trade_hub_id, eve_item_id, created_at, updated_at, quantity_to_produce, runs_count
  FROM production_lists pl_out
  WHERE user_id = $2