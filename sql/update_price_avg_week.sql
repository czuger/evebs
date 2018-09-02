/* il faut voir si on peut faire le calcul d'un coup ou bien s'il faut consolider les données de manière journalière d'abord */


UPDATE prices_advices pm SET ( price_avg_week, updated_at ) = ( mp, now() )
FROM (
       SELECT SUM( so.volume * so.price ) / SUM( so.volume ) mp, so.trade_hub_id ti, so.eve_item_id ei
       FROM sales_finals so
       WHERE so.day >= current_date - 7
         AND so.volume > 0
       GROUP BY so.trade_hub_id, so.eve_item_id ) min_so
WHERE ti = pm.trade_hub_id
AND ei = pm.eve_item_id;

UPDATE prices_advices cpa
SET price_avg_week = NULL, updated_at = now()
WHERE NOT EXISTS (
    SELECT 1 FROM sales_finals mp
    WHERE cpa.eve_item_id = mp.eve_item_id
       AND cpa.trade_hub_id = mp.trade_hub_id );