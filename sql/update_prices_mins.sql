-- Ne pas supprimer ces lignes, les garder, mais les marquer comme : old_prices.
-- en fait il faut mettre deux booleens pour dir qu'il s'agit de min prices de la semaine ou du mois (donc calculer le mois d'abord).
-- cela permet de monitorer les endroit ou il n'y a personne
-- dans un premier temps, on va garder le delete, s'il n'y a pas d'info, ça veut dire que personne n'a rien vendu depuis 1 mois
-- retention de sales order, pas la peine d'y aller.
-- par contre il fadudra afficher l'update date dans l'ecran des matériaux.

-- Update sales orders, flag closed for transaction that are not present from one retrieve session to another.
-- UPDATE sales_orders SET closed = true WHERE order_id IN (
-- SELECT order_id FROM sales_orders WHERE retrieve_session_id != ( SELECT MAX( retrieve_session_id ) FROM sales_orders )
-- EXCEPT
-- SELECT order_id FROM sales_orders WHERE retrieve_session_id = ( SELECT MAX( retrieve_session_id ) FROM sales_orders ) );
--
-- UPDATE sales_orders SET closed = true WHERE retrieve_session_id IS NULL;

-- Update min price data
DELETE FROM prices_mins pm WHERE NOT EXISTS (
    SELECT * FROM sales_orders so
    WHERE pm.trade_hub_id = so.trade_hub_id
    AND pm.eve_item_id = so.eve_item_id
    AND so.closed = false );

UPDATE prices_mins pm SET ( min_price, updated_at ) = ( mp, now() )
FROM (
       SELECT MIN( so.price ) mp, so.trade_hub_id ti, so.eve_item_id ei
       FROM sales_orders so
       WHERE so.closed = false
       GROUP BY so.trade_hub_id, so.eve_item_id ) min_so
WHERE ti = pm.trade_hub_id
      AND ei = pm.eve_item_id;

INSERT INTO prices_mins( trade_hub_id, eve_item_id, min_price, created_at, updated_at )
  SELECT trade_hub_id, eve_item_id, MIN( price ), now(), now()
  FROM sales_orders
  WHERE closed = false
AND NOT EXISTS (
SELECT * FROM prices_mins WHERE trade_hub_id = prices_mins.trade_hub_id AND eve_item_id = prices_mins.eve_item_id
)
GROUP BY trade_hub_id, eve_item_id;