class AddNewOrderToTradeOrder < ActiveRecord::Migration[4.2]
  def change
    add_column :trade_orders, :new_order, :boolean
  end
end
