class RenameUserSalesOrder < ActiveRecord::Migration[5.2]
  def change
    rename_table :user_sales_orders, :user_sale_orders if ActiveRecord::Base.connection.table_exists? 'user_sales_orders'

  end
end
