SELECT bpm_mat_ei.id, pl.user_id, bpm_mat_ei.name,
  SUM( raw_qtt ) - COALESCE( ba.quantity, 0 ) qtt_to_buy,
  ( SUM( raw_qtt ) - COALESCE( ba.quantity, 0 ) )*bpm_mat_ei.cost total_cost,
  ( SUM( raw_qtt ) - COALESCE( ba.quantity, 0 ) )*bpm_mat_ei.volume required_volume
FROM production_lists pl
  JOIN eve_items ei ON ei.id = pl.eve_item_id
  JOIN blueprints b ON ei.blueprint_id = b.id
  JOIN blueprint_materials bm ON b.id = bm.blueprint_id
  JOIN eve_items bpm_mat_ei ON bm.eve_item_id = bpm_mat_ei.id
  JOIN users ue ON pl.user_id = ue.id
  LEFT JOIN blueprint_modifications bmo ON b.id = bmo.blueprint_id AND bmo.user_id = pl.user_id
  LEFT JOIN bpc_assets ba ON bpm_mat_ei.id = ba.eve_item_id AND ba.station_detail_id = ue.selected_assets_station_id,
  LATERAL (SELECT required_qtt*runs_count*COALESCE( bmo.percent_modification_value, 1 )*1.05 AS raw_qtt) qtt_comp
WHERE runs_count IS NOT NULL
GROUP BY bpm_mat_ei.id, pl.user_id, bpm_mat_ei.name, COALESCE( ba.quantity, 0 )
HAVING SUM( raw_qtt ) - COALESCE( ba.quantity, 0 ) > 0;