class AddCppMarketPricesToEveItem < ActiveRecord::Migration[5.2]
  def change
    add_column :eve_items, :cpp_market_adjusted_price, :float
    add_column :eve_items, :cpp_market_average_price, :float
  end
end
