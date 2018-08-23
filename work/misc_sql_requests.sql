@required_quantities = @user.production_lists.where.not( runs_count: nil )
.joins( { eve_item: { blueprint_materials: :blueprint_component } }, { eve_item: :blueprint } )
.group( 'blueprint_components.id', 'blueprint_components.name' ).sum( 'required_qtt * runs_count' )


SELECT trade_hub_id, pl.eve_item_id, quantity_to_produce, runs_count, ei.name, nb_runs, prod_qtt, required_qtt, bc.name, bc.cost, required_qtt*bc.cost total_cost
FROM production_lists pl
  JOIN eve_items ei ON ei.id = pl.eve_item_id
  JOIN eve_items_users eiu ON ei.id = eiu.eve_item_id
  JOIN blueprints b ON ei.blueprint_id = b.id
  JOIN blueprint_materials bm ON b.id = bm.blueprint_id
  JOIN blueprint_components bc ON bm.blueprint_component_id = bc.id
WHERE runs_count IS NOT NULL
      AND eiu.user_id = 151;


SELECT bc.id, bc.name, SUM( CEIL( required_qtt*bmo.percent_modification_value )*runs_count ) - COALESCE( ba.quantity, 0 ) qtt_to_buy,
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
GROUP BY bc.id, bc.name, COALESCE( ba.quantity, 0 )
HAVING SUM( CEIL( required_qtt*bmo.percent_modification_value )*runs_count ) - COALESCE( ba.quantity, 0 ) > 0;


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

INSERT INTO production_lists( user_id, trade_hub_id, eve_item_id, created_at, updated_at, quantity_to_produce, runs_count )
  SELECT 153, trade_hub_id, eve_item_id, created_at, updated_at, quantity_to_produce, runs_count
  FROM production_lists pl_out
  WHERE user_id = 151
        AND NOT EXISTS( SELECT 1 FROM production_lists pl_in
  WHERE pl_in.trade_hub_id = pl_out.trade_hub_id AND pl_in.eve_item_id = pl_out.eve_item_id AND pl_in.user_id = pl_out.user_id )



INSERT INTO prices_advices( eve_item_id, region_id, trade_hub_id, created_at, updated_at )
  SELECT eve_items.id, trade_hubs.region_id, trade_hubs.id, now(), now()
  FROM eve_items, trade_hubs, blueprints
  WHERE eve_items.blueprint_id = blueprints.id
        AND NOT EXISTS (
      SELECT NULL FROM prices_advices pa, sales_finals sf
      WHERE pa.eve_item_id = eve_items.id
            AND pa.trade_hub_id = trade_hubs.id
            AND sf.eve_item_id = pa.eve_item_id
            AND sf.trade_hub_id = pa.trade_hub_id );

select 1;

Le faire avec un left join
UPDATE prices_advices pm SET ( price_avg_week, updated_at ) =
(
  SELECT SUM( so.volume * so.price ) / SUM( so.volume ) mp, now()
  FROM sales_finals so
  WHERE so.day >= current_date - 7
        AND so.trade_hub_id = pm.trade_hub_id
        AND so.eve_item_id = pm.eve_item_id
  GROUP BY so.trade_hub_id, so.eve_item_id
);

UPDATE prices_advices pm SET ( price_avg_week, updated_at ) = ( mp, now() )
FROM (
       SELECT SUM( so.volume * so.price ) / SUM( so.volume ) mp, so.trade_hub_id ti, so.eve_item_id ei
       FROM sales_finals so
       WHERE so.day >= current_date - 7
       GROUP BY so.trade_hub_id, so.eve_item_id ) min_so
  LEFT JOIN min_so ON min_so.ti = pm.trade_hub_id AND min_so.ei = pm.eve_item_id;

select distinct day, sum( volume ) from sales_finals GROUP BY day ORDER BY day;

select distinct day, count( * ) from sales_finals GROUP BY day ORDER BY day;

select min( updated_at ) from bpc_jita_sales_finals;

select min( updated_at ) from sales_finals;

select distinct day, sum( volume ) from sales_finals GROUP BY day ORDER BY day;

select count( * ) from blueprint_components where cost is null;

select count( * ) from prices_mins;

INSERT INTO prices_mins( trade_hub_id, eve_item_id, min_price, created_at, updated_at )
  SELECT trade_hub_id, eve_item_id, MIN( price ), now(), now()
  FROM sales_orders
  WHERE NOT EXISTS (
      SELECT * FROM prices_mins WHERE trade_hub_id = prices_mins.trade_hub_id AND eve_item_id = prices_mins.eve_item_id
  )
  GROUP BY trade_hub_id, eve_item_id;

SELECT SUM( so.volume ) mp, AVG( price ) ap, so.trade_hub_id ti, so.eve_item_id ei
FROM sales_finals so
GROUP BY so.trade_hub_id, so.eve_item_id
ORDER BY SUM( so.volume ) desc;

SELECT bc.id, pl.user_id, bc.name, SUM( CEIL( required_qtt*COALESCE( bmo.percent_modification_value, 1 ) )*runs_count ) - SUM( COALESCE( ba.quantity, 0 ) ) qtt_to_buy
FROM production_lists pl
  JOIN eve_items ei ON ei.id = pl.eve_item_id
  JOIN blueprints b ON ei.blueprint_id = b.id
  JOIN blueprint_materials bm ON b.id = bm.blueprint_id
  JOIN blueprint_components bc ON bm.blueprint_component_id = bc.id
  LEFT JOIN blueprint_modifications bmo ON b.id = bmo.blueprint_id AND bmo.user_id = pl.user_id
  LEFT JOIN bpc_assets ba ON bc.id = ba.blueprint_component_id
WHERE runs_count IS NOT NULL
GROUP BY bc.id, pl.user_id, bc.name
HAVING SUM( CEIL( required_qtt*COALESCE( bmo.percent_modification_value, 1 ) )*runs_count ) - COALESCE( ba.quantity, 0 ) > 0;


S