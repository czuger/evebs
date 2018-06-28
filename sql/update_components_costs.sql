UPDATE blueprint_components bc SET ( cost, updated_at ) = ( mc, now() )
FROM (
       SELECT SUM( volume * price ) / SUM( volume ) mc, blueprint_component_id bci
       FROM bpc_jita_sales_finals
       GROUP BY blueprint_component_id ) min_so
WHERE bci = bc.id;