/* il faut voir si on peut faire le calcul d'un coup ou bien s'il faut consolider les données de manière journalière d'abord */

/* Removing advices for items that are not in DB anymore */
-- DELETE FROM prices_advices pm WHERE NOT EXISTS (
--     SELECT 1 FROM eve_items ei
--     WHERE pm.eve_item_id = ei.id );

DELETE FROM prices_advices
  WHERE EXISTS (
      SELECT 1 FROM prices_advices pa, eve_items ei
      WHERE pa.eve_item_id = ei.id
      AND ei.blueprint_id IS NULL
  );

/* Insert new regions / items */
INSERT INTO prices_advices( eve_item_id, trade_hub_id, created_at, updated_at )
   SELECT DISTINCT sf.eve_item_id, sf.trade_hub_id, now(), now()
   FROM sales_finals sf, eve_items ei
     WHERE ei.id = sf.eve_item_id
      AND ei.blueprint_id IS NOT NULL
      AND NOT EXISTS (
        SELECT 1 FROM prices_advices pa, eve_items ei
        WHERE sf.eve_item_id = pa.eve_item_id
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