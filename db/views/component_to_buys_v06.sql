SELECT bc.id, pl.user_id, bc.name, SUM( CEIL( required_qtt*COALESCE( bmo.percent_modification_value, 1 ) )*runs_count ) - COALESCE( ba.quantity, 0 ) qtt_to_buy,
                                   ( SUM( CEIL( required_qtt*COALESCE( bmo.percent_modification_value, 1 ) )*runs_count ) - COALESCE( ba.quantity, 0 ) )*bc.cost total_cost,
                                   ( SUM( CEIL( required_qtt*COALESCE( bmo.percent_modification_value, 1 ) )*runs_count ) - COALESCE( ba.quantity, 0 ) )*bc.volume required_volume
FROM production_lists pl
  JOIN eve_items ei ON ei.id = pl.eve_item_id
  JOIN blueprints b ON ei.blueprint_id = b.id
  JOIN blueprint_materials bm ON b.id = bm.blueprint_id
  JOIN eve_business_server_dev.public.eve_items bc ON bm.eve_item_id = bc.id
  JOIN users ue ON pl.user_id = ue.id
  LEFT JOIN blueprint_modifications bmo ON b.id = bmo.blueprint_id AND bmo.user_id = pl.user_id
  LEFT JOIN bpc_assets ba ON bc.id = ba.eve_item_id AND ba.station_detail_id = ue.selected_assets_station_id
WHERE runs_count IS NOT NULL
GROUP BY bc.id, pl.user_id, bc.name, COALESCE( ba.quantity, 0 )
HAVING SUM( CEIL( required_qtt*COALESCE( bmo.percent_modification_value, 1 ) )*runs_count ) - COALESCE( ba.quantity, 0 ) > 0;