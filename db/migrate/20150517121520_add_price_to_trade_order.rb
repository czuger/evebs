class AddPriceToTradeOrder < ActiveRecord::Migration[4.2]
  def change
    add_column :trade_orders, :price, :float
  end
end
