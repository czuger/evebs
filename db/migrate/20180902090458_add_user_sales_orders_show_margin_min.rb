class AddUserSalesOrdersShowMarginMin < ActiveRecord::Migration[5.2]
  def change
    add_column :users, :sales_orders_show_margin_min, :integer
  end
end
