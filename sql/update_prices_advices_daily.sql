/* il faut voir si on peut faire le calcul d'un coup ou bien s'il faut consolider les données de manière journalière d'abord */

/* Removing advices for items that are not in DB anymore */
-- DELETE FROM prices_advices pm WHERE NOT EXISTS (
--     SELECT 1 FROM eve_items ei
--     WHERE pm.eve_item_id = ei.id );

/* Insert new regions / items */
INSERT INTO prices_advices( eve_item_id, trade_hub_id, created_at, updated_at )
   SELECT eve_items.id, trade_hubs.id, now(), now()
   FROM eve_items, trade_hubs, blueprints
   WHERE eve_items.blueprint_id = blueprints.id
       AND NOT EXISTS (
     SELECT NULL FROM prices_advices pa, sales_finals sf
     WHERE pa.eve_item_id = eve_items.id
       AND pa.trade_hub_id = trade_hubs.id
       AND sf.eve_item_id = pa.eve_item_id
       AND sf.trade_hub_id = pa.trade_hub_id );

UPDATE prices_advices pa SET ( vol_month, avg_price_month, updated_at ) = ( mp, ap, now() )
FROM (
       SELECT SUM( so.volume ) mp, AVG( price ) ap, so.trade_hub_id ti, so.eve_item_id ei
       FROM sales_finals so
       GROUP BY so.trade_hub_id, so.eve_item_id ) min_so
WHERE ti = pa.trade_hub_id
      AND ei = pa.eve_item_id;

UPDATE prices_advices pm SET ( avg_price_week, updated_at ) = ( mp, now() )
FROM (
       SELECT SUM( so.volume * so.price ) / SUM( so.volume ) mp, so.trade_hub_id ti, so.eve_item_id ei
       FROM sales_finals so
       WHERE so.day >= current_date - 7
         AND so.volume > 0
       GROUP BY so.trade_hub_id, so.eve_item_id ) min_so
WHERE ti = pm.trade_hub_id
AND ei = pm.eve_item_id;

UPDATE prices_advices cpa
SET avg_price_week = NULL, updated_at = now()
WHERE NOT EXISTS (
    SELECT 1 FROM sales_finals mp
    WHERE cpa.eve_item_id = mp.eve_item_id
       AND cpa.trade_hub_id = mp.trade_hub_id );