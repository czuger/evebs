class AddPkToCrestPricesLastMonthAverage < ActiveRecord::Migration
  def change
    add_column :crest_prices_last_month_averages, :id, :primary_key
  end
end
