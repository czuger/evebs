/* Don't forget to set the postgres sequence to cycle on production */
/* ALTER SEQUENCE caddie_crest_price_history_updates_id_seq CYCLE; */

/* TRUNCATE TABLE caddie_crest_price_history_updates; */

/* Removing advices for which we have no sales data */
DELETE FROM prices_advices pm WHERE NOT EXISTS (
    SELECT * FROM sales_finals so
    WHERE pm.trade_hub_id = so.trade_hub_id
          AND pm.eve_item_id = so.eve_item_id );

/* Insert new regions / items */
INSERT INTO prices_advices( eve_item_id, region_id, trade_hub_id, created_at, updated_at )
  SELECT eve_items.id, trade_hubs.region_id, trade_hubs.id, now(), now()
  FROM eve_items, trade_hubs, blueprints
  WHERE eve_items.blueprint_id = blueprints.id
      AND NOT EXISTS (
      SELECT NULL FROM prices_advices pa, sales_finals sf
      WHERE pa.eve_item_id = eve_items.id
            AND pa.trade_hub_id = trade_hubs.id
            AND sf.eve_item_id = eve_items.id
            AND sf.trade_hub_id = trade_hubs.id );

/* Update all data */
UPDATE prices_advices pm SET ( vol_month, vol_day, avg_price, updated_at ) = ( mp, mp/30, ap, now() )
FROM (
       SELECT SUM( so.volume ) mp, AVG( price ) ap, so.trade_hub_id ti, so.eve_item_id ei
       FROM sales_finals so
       GROUP BY so.trade_hub_id, so.eve_item_id ) min_so
WHERE ti = pm.trade_hub_id
AND ei = pm.eve_item_id;

-- UPDATE prices_advices cpa
-- SET vol_month = cplma.volume_sum, vol_day = floor( cplma.volume_sum / 30 ), avg_price = cplma.avg_price_avg,
-- updated_at = now()
-- FROM crest_prices_last_month_averages cplma, trade_hubs th
-- WHERE cpa.eve_item_id = cplma.eve_item_id
-- AND cpa.trade_hub_id = th.id
-- AND th.region_id = cplma.region_id;

-- start min prices update

UPDATE prices_advices cpa
SET min_price = mp.min_price, updated_at = now()
FROM prices_mins mp
WHERE cpa.eve_item_id = mp.eve_item_id
AND cpa.trade_hub_id = mp.trade_hub_id;

UPDATE prices_advices cpa
SET min_price = NULL, updated_at = now()
WHERE NOT EXISTS (
    SELECT NULL FROM prices_mins mp
    WHERE cpa.eve_item_id = mp.eve_item_id
          AND cpa.trade_hub_id = mp.trade_hub_id );

-- end min prices update

UPDATE prices_advices cpa
SET cost = ei.cost, updated_at = now()
FROM eve_items ei
WHERE cpa.eve_item_id = ei.id;

UPDATE prices_advices cpa
SET full_batch_size = bp.nb_runs*bp.prod_qtt, prod_qtt = bp.prod_qtt, updated_at = now()
FROM eve_items ei, blueprints bp
WHERE cpa.eve_item_id = ei.id
AND ei.blueprint_id = bp.id;

-- TODO : set the cost using the blueprint variable (see update_components_costs)
UPDATE prices_advices cpa SET single_unit_cost = cost/prod_qtt, updated_at = now();

UPDATE prices_advices cpa
SET daily_monthly_pcent = min_price / avg_price, updated_at = now();