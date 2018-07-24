class AddTouchedToSalesOrders < ActiveRecord::Migration[5.2]
  def change
    add_column :sales_orders, :touched, :boolean, null: false, default: false
    remove_column :sales_orders, :closed
    remove_column :sales_orders, :retrieve_session_id

    execute 'DROP SEQUENCE sales_orders_retrieve_session_id;'
  end
end
