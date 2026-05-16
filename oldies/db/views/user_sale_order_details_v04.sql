SELECT uso.id, user_id, tu.name || ' (' || r.name || ')' trade_hub_name,
       ei.name eve_item_name, price my_price, min_price, cost, prod_qtt,
  min_price / cost - 1 min_price_margin_pcent, min_price - price price_delta,
  uso.eve_item_id, uso.trade_hub_id, ei.cpp_eve_item_id, tu.eve_system_id
FROM user_sales_orders uso
  JOIN eve_items ei ON ei.id = uso.eve_item_id
  JOIN blueprints b ON ei.blueprint_id = b.id
  JOIN trade_hubs tu ON uso.trade_hub_id = tu.id
  JOIN regions r ON tu.region_id = r.id
  LEFT JOIN prices_mins pm ON pm.eve_item_id = uso.eve_item_id AND pm.trade_hub_id = uso.trade_hub_id


-- LATERAL(SELECT cost / prod_qtt) AS s1(unit_cost)