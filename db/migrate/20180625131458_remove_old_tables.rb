class RemoveOldTables < ActiveRecord::Migration[5.2]
  def change
    drop_table :crest_prices_last_month_averages
    drop_table :eve_empty_market_histories
    drop_table 'eve_market_history_archives'
    drop_table 'eve_market_history_errors'
    drop_table 'eve_markets_histories'
    drop_table 'eve_markets_prices'
  end
end
