class RenameSaleOrderToSalesOrder < ActiveRecord::Migration[5.2]
  def change
    rename_table :sale_orders, :sales_orders
  end
end
