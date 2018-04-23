class RenameCrestPriceHistoryToEveMarketsHistory < ActiveRecord::Migration[5.2]
  def change
    rename_table :crest_price_histories, :eve_markets_histories
  end
end
