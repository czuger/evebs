class RemoveOrderIdIndexOnSaleOrder < ActiveRecord::Migration[5.2]
  def change
    remove_index :sale_orders, :order_id
  end
end
