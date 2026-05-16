-- UPDATE eve_items ei SET ( cost, updated_at ) = ( avg_price, now() )
-- FROM (
--        SELECT SUM( sf.volume * sf.price ) / SUM( sf.volume ) avg_price, sf.eve_item_id ei
--        FROM sales_finals sf
--          JOIN trade_hubs tu ON sf.trade_hub_id = tu.id
--        WHERE sf.day >= current_date - 7
--              AND sf.volume > 0
--              AND tu.eve_system_id = '30000142'
--        GROUP BY sf.eve_item_id ) min_so
-- WHERE ei = ei.id
--       AND ei.base_item = true;

-- For base items, the cost is now the newly weekly computed price.
UPDATE eve_items ei SET ( cost, updated_at ) = ( weekly_avg_price, now() )
  WHERE ei.base_item = TRUE;