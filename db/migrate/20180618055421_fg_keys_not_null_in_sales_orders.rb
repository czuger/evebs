class FgKeysNotNullInSalesOrders < ActiveRecord::Migration[5.2]
  def change
    change_column :sales_orders, :trade_hub_id, :bigint, null: false
    change_column :sales_orders, :eve_item_id, :bigint, null: false

    remove_column :sales_orders, :cpp_system_id
    remove_column :sales_orders, :cpp_type_id
  end
end
