UPDATE
  prices_advices
SET
  vol_month = te.volume_total
FROM
  trade_volume_estimations te, trade_hubs tu, universe_systems us
WHERE
  prices_advices.eve_item_id = te.eve_item_id
AND prices_advices.trade_hub_id = tu.id
AND tu.eve_system_id = us.cpp_system_id
AND te.universe_system_id = us.id;