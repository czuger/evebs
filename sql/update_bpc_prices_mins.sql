DELETE FROM bpc_prices_mins pm WHERE NOT EXISTS (
    SELECT 1 FROM blueprint_component_sales_orders so
    WHERE pm.trade_hub_id = so.trade_hub_id
    AND pm.blueprint_component_id = so.blueprint_component_id );

UPDATE bpc_prices_mins pm SET ( price, updated_at ) = ( mp, now() )
FROM (
       SELECT MIN( so.price ) mp, so.trade_hub_id ti, so.blueprint_component_id ei
       FROM blueprint_component_sales_orders so
       GROUP BY so.trade_hub_id, so.blueprint_component_id ) min_so
WHERE ti = pm.trade_hub_id
AND ei = pm.blueprint_component_id;

INSERT INTO bpc_prices_mins( trade_hub_id, blueprint_component_id, price, created_at, updated_at )
  SELECT trade_hub_id, blueprint_component_id, MIN( price ), now(), now()
  FROM blueprint_component_sales_orders bcso
  WHERE NOT EXISTS (
    SELECT * FROM bpc_prices_mins WHERE bcso.trade_hub_id = bpc_prices_mins.trade_hub_id AND bcso.blueprint_component_id = bpc_prices_mins.blueprint_component_id
  )
GROUP BY trade_hub_id, blueprint_component_id;

UPDATE bpc_prices_mins pm SET volume = (
  SELECT MAX( so.volume ) mp
  FROM blueprint_component_sales_orders so
  WHERE so.trade_hub_id = pm.trade_hub_id
  AND so.blueprint_component_id = pm.blueprint_component_id
  AND so.price = pm.price );
