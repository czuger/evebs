class ChangeSalesOrderIssuedToDateTime < ActiveRecord::Migration[5.2]
  def change
    remove_column :sales_orders, :issued
    add_column :sales_orders, :issued, :timestamp

    remove_column :sales_orders, :end_time
    add_column :sales_orders, :end_time, :timestamp
  end
end
