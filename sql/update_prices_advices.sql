/* Don't forget to set the postgres sequence to cycle on production */
/* ALTER SEQUENCE caddie_crest_price_history_updates_id_seq CYCLE; */

/* TRUNCATE TABLE caddie_crest_price_history_updates; */

/* Removing advices for which we have no sales data */
DELETE FROM prices_advices pm WHERE NOT EXISTS (
    SELECT 1 FROM sales_finals so
    WHERE pm.trade_hub_id = so.trade_hub_id
          AND pm.eve_item_id = so.eve_item_id );

/* Removing advices for items that are not in DB anymore */
DELETE FROM prices_advices pm WHERE NOT EXISTS (
    SELECT 1 FROM eve_items ei
    WHERE pm.eve_item_id = ei.id );

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

/* Update all data */
UPDATE prices_advices pa SET ( vol_month, vol_day, avg_price_month, updated_at ) = ( mp, mp/30, ap, now() )
FROM (
       SELECT SUM( so.volume ) mp, AVG( price ) ap, so.trade_hub_id ti, so.eve_item_id ei
       FROM sales_finals so
       GROUP BY so.trade_hub_id, so.eve_item_id ) min_so
WHERE ti = pa.trade_hub_id
AND ei = pa.eve_item_id;

UPDATE prices_advices pa SET ( margin_percent, daily_monthly_pcent, updated_at ) = ( margin_percent, daily_monthly_pcent, now() )
FROM (
       SELECT ( min_price / (cost/prod_qtt) - 1 ) * 100 margin_percent,
         min_price / avg_price_month daily_monthly_pcent, sub_pa.trade_hub_id ti, sub_pa.eve_item_id ei
       FROM prices_advices sub_pa
         JOIN prices_mins pm ON pm.eve_item_id = sub_pa.eve_item_id AND pm.trade_hub_id = sub_pa.trade_hub_id
         JOIN eve_items ei ON ei.id = pm.eve_item_id
         JOIN blueprints bp ON ei.blueprint_id = bp.id
       GROUP BY sub_pa.trade_hub_id, sub_pa.eve_item_id ) min_so
WHERE ti = pa.trade_hub_id
      AND ei = pa.eve_item_id;