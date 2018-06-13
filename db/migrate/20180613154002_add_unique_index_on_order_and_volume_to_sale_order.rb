class AddUniqueIndexOnOrderAndVolumeToSaleOrder < ActiveRecord::Migration[5.2]
  def change
    add_index :sale_orders, [ :order_id, :volume ], unique: true
  end
end
