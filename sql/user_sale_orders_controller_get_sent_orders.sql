INSERT INTO user_sale_orders( user_id, trade_hub_id, eve_item_id, created_at, updated_at, price )
  SELECT $1, trade_hub_id, eve_item_id, created_at, now(), price
FROM user_sale_orders uso_out
WHERE user_id = $2