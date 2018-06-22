/* il faut voir si on peut faire le calcul d'un coup ou bien s'il faut consolider les données de manière journalière d'abord */

UPDATE prices_avg_weeks pm SET ( price, updated_at ) = ( mp, now() )
FROM (
       SELECT SUM( so.volume * so.price ) / SUM( so.volume ) mp, so.trade_hub_id ti, so.eve_item_id ei
       FROM sales_finals so
       WHERE so.day >= current_date - 7
       GROUP BY so.trade_hub_id, so.eve_item_id ) min_so
WHERE ti = pm.trade_hub_id
AND ei = pm.eve_item_id;

INSERT INTO prices_avg_weeks( trade_hub_id, eve_item_id, price, created_at, updated_at )
  SELECT so.trade_hub_id, so.eve_item_id, SUM( so.volume * so.price ) / SUM( so.volume ), now(), now()
  FROM sales_finals so
  WHERE so.eve_item_id = eve_item_id
        AND so.trade_hub_id = trade_hub_id
        AND so.day >= current_date - 7
        AND NOT EXISTS (
          SELECT 1 FROM prices_avg_weeks
          WHERE so.trade_hub_id = trade_hub_id
          AND so.eve_item_id = eve_item_id
        )
  GROUP BY so.trade_hub_id, so.eve_item_id;