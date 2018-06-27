UPDATE blueprint_components bc SET ( cost, updated_at ) = ( mc, now() )
FROM (
       SELECT MIN( price ) mc, blueprint_component_id bci
       FROM blueprint_component_sales_orders, trade_hubs
       WHERE trade_hubs.id = trade_hub_id
       AND eve_system_id = 30000142
       GROUP BY blueprint_component_id ) min_so
WHERE bci = bc.id;