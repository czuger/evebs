class AddIndexOnHistoryDateToCrestPriceHistories < ActiveRecord::Migration
  def change
    add_index :crest_price_histories, :history_date
  end
end
