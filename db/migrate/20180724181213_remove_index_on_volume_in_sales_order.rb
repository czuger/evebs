class RemoveIndexOnVolumeInSalesOrder < ActiveRecord::Migration[5.2]
  def change
    remove_index :sales_orders, [ :order_id, :volume ]
    add_index :sales_orders, :order_id, unique: true
  end
end
