UPDATE blueprint_components bc SET ( cost, updated_at ) = ( mc, now() )
FROM (
       SELECT ( ( SUM( volume * price ) / SUM( volume ) ) ) * $1 mc, blueprint_component_id bci
       FROM bpc_jita_sales_finals
       WHERE updated_at >= current_date - 7
       GROUP BY blueprint_component_id ) min_so
WHERE bci = bc.id;