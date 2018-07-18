INSERT INTO production_lists( user_id, trade_hub_id, eve_item_id, created_at, updated_at, quantity_to_produce, runs_count )
  SELECT $1, trade_hub_id, eve_item_id, created_at, updated_at, quantity_to_produce, runs_count
  FROM production_lists pl_out
  WHERE user_id = $2
        AND NOT EXISTS( SELECT 1 FROM production_lists pl_in
  WHERE pl_in.trade_hub_id = pl_out.trade_hub_id AND pl_in.eve_item_id = pl_out.eve_item_id AND pl_in.user_id = $1 )