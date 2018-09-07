/* il faut voir si on peut faire le calcul d'un coup ou bien s'il faut consolider les données de manière journalière d'abord */


UPDATE eve_items ei SET ( cost, updated_at ) = ( avg_price, now() )
FROM (
       SELECT SUM( so.volume * so.price ) / SUM( so.volume ) avg_price, so.eve_item_id ei
       FROM sales_finals so
         JOIN eve_business_server_dev.public.trade_hubs tu
       WHERE so.day >= current_date - 7
         AND so.volume > 0
       GROUP BY so.trade_hub_id, so.eve_item_id ) min_so
WHERE ti = pm.trade_hub_id
AND ei = pm.eve_item_id;
