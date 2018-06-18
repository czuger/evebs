class RenameMinPriceToPricesMin < ActiveRecord::Migration[5.2]
  def change
    rename_table :min_prices, :prices_mins
    drop_table :min_price_dailies
    drop_table :min_prices_logs
  end
end
