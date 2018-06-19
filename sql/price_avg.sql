/* il faut voir si on peut faire le calcul d'un coup ou bien s'il faut consolider les données de manière journalière d'abord */

BEGIN;

UPDATE price_avg_weeks paw SET ( price, updated_at ) = (
  SELECT SUM( so.volume * so.price ) / SUM( so.volume ),now()
  FROM sale_orders so, trade_hubs th, eve_items ei
  WHERE so.cpp_system_id = th.eve_system_id
  AND so.cpp_type_id = ei.cpp_eve_item_id
  AND th.id = paw.trade_hub_id
  AND ei.id = paw.eve_item_id
  AND so.day >= current_date - 7
  GROUP BY th.id, ei.id
  );

INSERT INTO price_avg_weeks
  SELECT nextval( 'eve_market_history_archives_id_seq' ), th.id, ei.id, SUM( so.volume * so.price ) / SUM( so.volume ), now(), now()
  FROM sale_orders so, trade_hubs th, eve_items ei
  WHERE so.cpp_system_id = th.eve_system_id
  AND so.cpp_type_id = ei.cpp_eve_item_id
  AND so.day >= current_date - 7
  AND NOT EXISTS (
        SELECT 1 FROM price_avg_weeks WHERE th.id = price_avg_weeks.trade_hub_id AND ei.id = price_avg_weeks.eve_item_id
    )
  GROUP BY th.id, ei.id;

COMMIT;