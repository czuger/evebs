INSERT INTO eve_market_histories_groups ( eve_item_id, universe_region_id, volume, highest, lowest, average, created_at, updated_at )
  SELECT ei.id, ur.id, mh.volume, mh.highest, mh.lowest, mh.average, now(), now()
  FROM eve_market_histories_group_tmp_tables mh, eve_items ei, universe_regions ur
  WHERE mh.cpp_type_id = ei.cpp_eve_item_id
    AND mh.cpp_region_id = ur.cpp_region_id
ON CONFLICT (eve_item_id, universe_region_id)
  DO UPDATE SET
    volume = EXCLUDED.volume,
    highest = EXCLUDED.highest,
    lowest = EXCLUDED.lowest,
    average = EXCLUDED.average,
    updated_at = now();

DELETE FROM eve_market_histories_groups mh WHERE NOT EXISTS (
    SELECT 1
    FROM eve_market_histories_group_tmp_tables mh_tmp, eve_items ei, universe_regions ur
    WHERE mh.eve_item_id = ei.id
      AND mh.universe_region_id = ur.id
      AND mh_tmp.cpp_type_id = ei.cpp_eve_item_id
      AND mh_tmp.cpp_region_id = ur.cpp_region_id );