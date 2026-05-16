SELECT bc.id, pl.user_id, bc.name, SUM( CEIL( required_qtt*COALESCE( bmo.percent_modification_value, 1 ) )*runs_count ) - COALESCE( ba.quantity, 0 ) qtt_to_buy,
                                   ( SUM( CEIL( required_qtt*COALESCE( bmo.percent_modification_value, 1 ) )*runs_count ) - COALESCE( ba.quantity, 0 ) )*bc.cost total_cost
FROM production_lists pl
  JOIN eve_items ei ON ei.id = pl.eve_item_id
  JOIN blueprints b ON ei.blueprint_id = b.id
  JOIN blueprint_materials bm ON b.id = bm.blueprint_id
  JOIN blueprint_components bc ON bm.blueprint_component_id = bc.id
  LEFT JOIN blueprint_modifications bmo ON b.id = bmo.blueprint_id AND bmo.user_id = pl.user_id
  LEFT JOIN bpc_assets ba ON bc.id = ba.blueprint_component_id
WHERE runs_count IS NOT NULL
GROUP BY bc.id, pl.user_id, bc.name, COALESCE( ba.quantity, 0 )
HAVING SUM( CEIL( required_qtt*COALESCE( bmo.percent_modification_value, 1 ) )*runs_count ) - COALESCE( ba.quantity, 0 ) > 0;