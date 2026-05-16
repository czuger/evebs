INSERT INTO eve_market_history_archives
  SELECT
  nextval( 'eve_market_history_archives_id_seq' ), region_id, eve_item_id, to_char( history_date, 'YYYY' ),
  to_char( history_date, 'MM' ), history_date, order_count,
           volume, low_price, avg_price, high_price, created_at, updated_at
           FROM eve_markets_histories
           WHERE NOT EXISTS (
             SELECT id FROM eve_market_history_archives WHERE
               eve_market_history_archives.region_id = eve_markets_histories.region_id AND
               eve_market_history_archives.eve_item_id = eve_markets_histories.eve_item_id AND
               eve_market_history_archives.history_date = eve_markets_histories.history_date
           );

-- DELETE FROM eve_markets_histories;

-- VACUUM FULL ANALYZE eve_markets_histories;