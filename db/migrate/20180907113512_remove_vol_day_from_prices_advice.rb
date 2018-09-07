class RemoveVolDayFromPricesAdvice < ActiveRecord::Migration[5.2]
  def change
    remove_column :prices_advices, :vol_day
  end
end
