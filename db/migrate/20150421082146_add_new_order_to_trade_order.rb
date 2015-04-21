class AddNewOrderToTradeOrder < ActiveRecord::Migration
  def change
    add_column :trade_orders, :new_order, :boolean
  end
end
