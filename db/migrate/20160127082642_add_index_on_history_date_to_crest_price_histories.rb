class AddIndexOnHistoryDateToCrestPriceHistories < ActiveRecord::Migration[4.2]
  def change
    add_index :crest_price_histories, :history_date
  end
end
