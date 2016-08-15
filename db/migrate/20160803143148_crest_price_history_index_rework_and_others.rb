class CrestPriceHistoryIndexReworkAndOthers < ActiveRecord::Migration
  def change

    # remove_column :crest_price_histories, :day_timestamp

    remove_index :crest_price_histories, :eve_item_id
    remove_index :crest_price_histories, :region_id
    remove_index :crest_price_histories, :history_date
    # remove_index :crest_price_histories, name: :price_histories_all_keys_index

    add_index :crest_price_histories, [ :region_id, :eve_item_id ], name: :index_crest_price_histories_on_region_and_item
    add_index :crest_price_histories, :history_date

    remove_index :crest_prices_last_month_averages, name: :prices_lmavg_all_keys_index

  end
end
