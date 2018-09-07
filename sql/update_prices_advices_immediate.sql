/* Removing advices for which we have no sales data */
DELETE FROM prices_advices pm WHERE NOT EXISTS (
    SELECT 1 FROM sales_finals so
    WHERE pm.trade_hub_id = so.trade_hub_id
          AND pm.eve_item_id = so.eve_item_id );

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

UPDATE prices_advices pa SET ( margin_percent, immediate_montly_pcent, updated_at ) = ( min_so.margin_percent, daily_monthly_pcent, now() )
FROM (
       SELECT ( min_price / cost - 1 ) * 100 margin_percent,
         min_price / avg_price_month daily_monthly_pcent, sub_pa.trade_hub_id ti, sub_pa.eve_item_id ei
       FROM prices_advices sub_pa
         JOIN prices_mins pm ON pm.eve_item_id = sub_pa.eve_item_id AND pm.trade_hub_id = sub_pa.trade_hub_id
         JOIN eve_items ei ON ei.id = pm.eve_item_id
         JOIN blueprints bp ON ei.blueprint_id = bp.id ) min_so
WHERE ti = pa.trade_hub_id
      AND ei = pa.eve_item_id;