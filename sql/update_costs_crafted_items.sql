UPDATE eve_items ei SET ( cost, updated_at ) = ( comp_cost, now() )
FROM (
       SELECT ( SUM( required_qtt * COALESCE( material_ei.cost, 'Infinity' ) ) * constants.f_value ) / prod_qtt "comp_cost", comp_ei.id
       FROM constants, eve_items comp_ei
         JOIN blueprints b ON comp_ei.blueprint_id = b.id
         JOIN blueprint_materials bm ON b.id = bm.blueprint_id
         JOIN eve_items material_ei ON bm.eve_item_id = material_ei.id
       WHERE constants.libe = 'taxes'
       GROUP BY comp_ei.id, prod_qtt, constants.f_value
     ) ei_cost_comp
WHERE ei_cost_comp.id = ei.id
      AND ei.production_level = $1
      AND ei.base_item = FALSE;
