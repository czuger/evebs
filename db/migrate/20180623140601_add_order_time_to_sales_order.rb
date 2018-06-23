class AddOrderTimeToSalesOrder < ActiveRecord::Migration[5.2]
  def change
    add_column :sales_orders, :issued, :time
    add_column :sales_orders, :duration, :integer
    add_column :sales_orders, :end_time, :time
  end
end
