/* Updating regions id */
UPDATE trade_volume_estimations
SET
  cpp_region_id = ur.cpp_region_id
FROM universe_regions ur, universe_constellations uc, universe_systems us
WHERE ur.id = uc.universe_region_id
AND uc.id = us.universe_constellation_id
AND us.cpp_system_id = trade_volume_estimations.cpp_system_id;

/* Summing region volumes */
UPDATE trade_volume_estimations tve SET ( region_volume_computed_from_orders, updated_at ) =
( sub_tve.volume, now() )
FROM (
       SELECT SUM( trade_hub_volume_computed_from_orders ) volume, cpp_region_id, cpp_type_id
       FROM trade_volume_estimations
       GROUP BY cpp_region_id, cpp_type_id ) sub_tve
WHERE tve.cpp_region_id = sub_tve.cpp_region_id
AND tve.cpp_type_id = sub_tve.cpp_type_id;

/* Adjusting percentage */
UPDATE trade_volume_estimations SET trade_hub_to_region_percentage_computed_from_orders =
CAST( trade_hub_volume_computed_from_orders AS FLOAT ) / region_volume_computed_from_orders;

/* Adjusting final trade_hub volume */
UPDATE trade_volume_estimations SET trade_hub_volume_adjusted_from_percentage =
trade_hub_to_region_percentage_computed_from_orders * region_volume_downloaded_from_history;

/* Updating volume in prices_advices */
UPDATE
  prices_advices
SET
  vol_month = te.trade_hub_volume_adjusted_from_percentage, updated_at = now()
FROM
  trade_volume_estimations te, trade_hubs tu, eve_items ei
WHERE
  prices_advices.eve_item_id = ei.id
  AND prices_advices.trade_hub_id = tu.id
  AND tu.eve_system_id = te.cpp_system_id
  AND ei.cpp_eve_item_id = te.cpp_type_id;
