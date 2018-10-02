/* Removing advices for which we have no sales data */
UPDATE prices_advices pm SET ( vol_month, avg_price_month, immediate_montly_pcent, margin_percent, avg_price_week, updated_at ) =
( null, null, null, null, null, now() )
WHERE NOT EXISTS (
    SELECT 1 FROM sales_finals so
    WHERE pm.trade_hub_id = so.trade_hub_id
          AND pm.eve_item_id = so.eve_item_id );

UPDATE prices_advices pa SET ( margin_percent, immediate_montly_pcent, updated_at ) = ( min_so.margin_percent, daily_monthly_pcent, now() )
FROM (
       SELECT ( min_price / cost - 1 ) margin_percent,
         min_price / avg_price_month daily_monthly_pcent, sub_pa.trade_hub_id ti, sub_pa.eve_item_id ei
       FROM prices_advices sub_pa
         JOIN prices_mins pm ON pm.eve_item_id = sub_pa.eve_item_id AND pm.trade_hub_id = sub_pa.trade_hub_id
         JOIN eve_items ei ON ei.id = pm.eve_item_id
         JOIN blueprints bp ON ei.blueprint_id = bp.id ) min_so
WHERE ti = pa.trade_hub_id
      AND ei = pa.eve_item_id;