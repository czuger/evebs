class AddPriceToTradeOrder < ActiveRecord::Migration
  def change
    add_column :trade_orders, :price, :float
  end
end
