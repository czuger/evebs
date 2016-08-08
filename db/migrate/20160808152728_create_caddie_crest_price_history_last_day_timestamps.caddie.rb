# This migration comes from caddie (originally 20160803094530)
class CreateCaddieCrestPriceHistoryLastDayTimestamps < ActiveRecord::Migration
  def change
    create_table :caddie_crest_price_history_last_day_timestamps do |t|
      t.references :eve_item, index: false, foreign_key: true
      t.references :region, index: false, foreign_key: true
      t.datetime :day_timestamp

      t.timestamps null: false
    end
    add_index :caddie_crest_price_history_last_day_timestamps, [ :region_id, :eve_item_id ], unique: true, name: :index_caddie_crest_price_history_last_day_timestamps
  end
end
