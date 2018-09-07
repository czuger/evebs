/* il faut voir si on peut faire le calcul d'un coup ou bien s'il faut consolider les données de manière journalière d'abord */

UPDATE eve_items ei SET ( cost, updated_at ) = ( avg_price, now() )
FROM (
       SELECT SUM( sf.volume * sf.price ) / SUM( sf.volume ) avg_price, sf.eve_item_id ei
       FROM sales_finals sf
         JOIN trade_hubs tu ON sf.trade_hub_id = tu.id
       WHERE sf.day >= current_date - 7
             AND sf.volume > 0
             AND tu.eve_system_id = '30000142'
       GROUP BY sf.eve_item_id ) min_so
WHERE ei = ei.id
      AND ei.base_item = true;