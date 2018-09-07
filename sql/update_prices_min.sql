-- Ne pas supprimer ces lignes, les garder, mais les marquer comme : old_prices.
-- en fait il faut mettre deux booleens pour dir qu'il s'agit de min prices de la semaine ou du mois (donc calculer le mois d'abord).
-- cela permet de monitorer les endroit ou il n'y a perptonne
-- dans un premier temps, on va garder le delete, s'il n'y a pas d'info, ça veut dire que perptonne n'a rien vendu depuis 1 mois
-- retention de sales order, pas la peine d'y aller.
-- par contre il fadudra afficher l'update date dans l'ecran des matériaux.

-- Update sales orders, flag closed for transaction that are not present from one retrieve session to another.
-- UPDATE public_trade_orders SET closed = true WHERE order_id IN (
-- SELECT order_id FROM public_trade_orders WHERE retrieve_session_id != ( SELECT MAX( retrieve_session_id ) FROM public_trade_orders )
-- EXCEPT
-- SELECT order_id FROM public_trade_orders WHERE retrieve_session_id = ( SELECT MAX( retrieve_session_id ) FROM public_trade_orders ) );
--
-- UPDATE public_trade_orders SET closed = true WHERE retrieve_session_id IS NULL;

-- Update min price data
DELETE FROM prices_mins pm WHERE NOT EXISTS (
    SELECT * FROM public_trade_orders pto
    WHERE pm.trade_hub_id = pto.trade_hub_id
    AND pm.eve_item_id = pto.eve_item_id
    AND pto.is_buy_order = FALSE );

INSERT INTO prices_mins ( trade_hub_id, eve_item_id, min_price, created_at, updated_at )
  SELECT trade_hub_id, eve_item_id, MIN( price ), now(), now()
  FROM public_trade_orders pto
    WHERE pto.is_buy_order = FALSE
  GROUP BY trade_hub_id, eve_item_id
ON CONFLICT (trade_hub_id, eve_item_id)
  DO UPDATE SET
    min_price = EXCLUDED.min_price,
    updated_at = now();

UPDATE prices_mins pm SET ( volume, updated_at ) = ( volume_sub.volume, now() )
FROM (
    SELECT SUM( volume ) volume, trade_hub_id, eve_item_id
    FROM prices_mins sub_pm
    GROUP BY trade_hub_id, eve_item_id ) volume_sub
WHERE pm.trade_hub_id = volume_sub.trade_hub_id
AND pm.eve_item_id = volume_sub.eve_item_id;