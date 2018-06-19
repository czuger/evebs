/* il faut voir si on peut faire le calcul d'un coup ou bien s'il faut consolider les données de manière journalière d'abord */

-- Bad explain plan
-- UPDATE price_avg_weeks paw SET ( price, updated_at ) = (
--   SELECT SUM( so.volume * so.price ) / SUM( so.volume ),now()
--   FROM sales_finals so
--   WHERE so.eve_item_id = paw.eve_item_id
--         AND so.trade_hub_id = paw.trade_hub_id
--         AND so.day >= current_date - 7
--   GROUP BY paw.eve_item_id, paw.trade_hub_id
-- );

INSERT INTO price_avg_weeks
  SELECT nextval( 'eve_market_history_archives_id_seq' ), so.trade_hub_id, so.eve_item_id, SUM( so.volume * so.price ) / SUM( so.volume ), now(), now()
  FROM sales_finals so
  WHERE so.eve_item_id = eve_item_id
        AND so.trade_hub_id = trade_hub_id
        AND so.day >= current_date - 7
        AND NOT EXISTS (
      SELECT 1 FROM price_avg_weeks
      WHERE so.trade_hub_id = price_avg_weeks.trade_hub_id
            AND so.eve_item_id = price_avg_weeks.eve_item_id
  )
  GROUP BY so.eve_item_id, so.trade_hub_id