class AddPriceAvgWeekToPricesAdvice < ActiveRecord::Migration[5.2]
  def change
    add_column :prices_advices, :price_avg_week, :float
    drop_table :prices_avg_weeks
  end
end
