class RenamePriceAvgWeekToPricesAvgWeek < ActiveRecord::Migration[5.2]
  def change
    rename_table :price_avg_weeks, :prices_avg_weeks
  end
end
