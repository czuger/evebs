SELECT bc.id, eiu.user_id, bc.name, SUM( CEIL( required_qtt*bmo.percent_modification_value )*runs_count ) - COALESCE( ba.quantity, 0 ) qtt_to_buy,
  ( SUM( CEIL( required_qtt*bmo.percent_modification_value )*runs_count ) - COALESCE( ba.quantity, 0 ) )*bc.cost total_cost
FROM production_lists pl
  JOIN eve_items ei ON ei.id = pl.eve_item_id
  JOIN eve_items_users eiu ON ei.id = eiu.eve_item_id
  JOIN blueprints b ON ei.blueprint_id = b.id
  JOIN blueprint_materials bm ON b.id = bm.blueprint_id
  JOIN blueprint_components bc ON bm.blueprint_component_id = bc.id
  JOIN blueprint_modifications bmo ON b.id = bmo.blueprint_id AND bmo.user_id = eiu.user_id
  LEFT JOIN bpc_assets ba ON bc.id = ba.blueprint_component_id
WHERE runs_count IS NOT NULL
GROUP BY bc.id, eiu.user_id, bc.name, COALESCE( ba.quantity, 0 )
HAVING SUM( CEIL( required_qtt*bmo.percent_modification_value )*runs_count ) - COALESCE( ba.quantity, 0 ) > 0;