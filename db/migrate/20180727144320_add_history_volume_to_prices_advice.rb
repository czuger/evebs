class AddHistoryVolumeToPricesAdvice < ActiveRecord::Migration[5.2]
  def change
    add_column :prices_advices, :history_volume, :bigint
  end
end
