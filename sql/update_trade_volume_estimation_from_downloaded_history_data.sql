UPDATE trade_volume_estimations tve SET ( region_volume_downloaded_from_history, updated_at ) = ( volume, now() )
  FROM eve_market_histories_group_tmp_tables eh_tmp
  WHERE tve.cpp_type_id = eh_tmp.cpp_type_id
  AND tve.cpp_region_id = eh_tmp.cpp_region_id;