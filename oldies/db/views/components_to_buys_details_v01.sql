SELECT pl.id, pl.user_id, b.cpp_blueprint_id, b.id bp_id, b.name bp_name,
                                              bpm_mat_ei.id mat_id, bpm_mat_ei.name mat_name,
  required_qtt, coalesce( bmo.percent_modification_value, 1 ) bp_reduction
FROM production_lists pl
  JOIN eve_items ei ON ei.id = pl.eve_item_id
  JOIN blueprints b ON ei.blueprint_id = b.id
  JOIN blueprint_materials bm ON b.id = bm.blueprint_id
  JOIN eve_items bpm_mat_ei ON bm.eve_item_id = bpm_mat_ei.id
  JOIN users ue ON pl.user_id = ue.id
  LEFT JOIN blueprint_modifications bmo ON b.id = bmo.blueprint_id AND bmo.user_id = pl.user_id
WHERE runs_count > 0;