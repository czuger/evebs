UPDATE sales_orders SET trade_hub_id = (SELECT id FROM trade_hubs WHERE eve_system_id = cpp_system_id);

UPDATE sales_orders SET eve_item_id = (SELECT id FROM eve_items WHERE cpp_type_id = cpp_eve_item_id);