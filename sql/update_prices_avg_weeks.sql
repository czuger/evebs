INSERT INTO weekly_price_details ( eve_item_id, day, volume, weighted_avg_price, created_at, updated_at )
  SELECT sf.eve_item_id ei, day, SUM( sf.volume ), SUM( sf.volume * sf.price ) / SUM( sf.volume ), now(), now()
  FROM sales_finals sf
    JOIN trade_hubs tu ON sf.trade_hub_id = tu.id
      WHERE sf.day >= current_date - 7
        AND sf.volume > 0
        AND tu.eve_system_id = '30000142'
  GROUP BY sf.eve_item_id, day
ON CONFLICT (eve_item_id, day)
  DO UPDATE SET
    volume = EXCLUDED.volume,
    weighted_avg_price = EXCLUDED.weighted_avg_price,
    updated_at = now();

UPDATE eve_items ei SET ( weekly_avg_price, updated_at ) = ( wap, now() )
FROM (
       SELECT SUM( wpd.volume * wpd.weighted_avg_price ) / SUM( wpd.volume ) wap, wpd.eve_item_id ei
       FROM weekly_price_details wpd
       GROUP BY wpd.eve_item_id ) weekly_avg
WHERE ei = ei.id;