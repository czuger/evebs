UPDATE eve_items ei SET ( cost, updated_at ) = ( comp_cost, now() )
FROM (
       SELECT ( SUM( required_qtt * 0.94 * material_ei.cost ) * 1.03 ) / prod_qtt "comp_cost", comp_ei.id
       FROM eve_items comp_ei
         JOIN blueprints b ON comp_ei.blueprint_id = b.id
         JOIN blueprint_materials bm ON b.id = bm.blueprint_id
         JOIN eve_items material_ei ON bm.eve_item_id = material_ei.id
       GROUP BY comp_ei.id, prod_qtt
     ) ei_cost_comp
WHERE ei_cost_comp.id = ei.id
      AND ei.production_level = $1
      AND ei.base_item = FALSE;
