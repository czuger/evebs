class CreateCrestPricesLastMonthAverages < ActiveRecord::Migration
  def change
    create_table :crest_prices_last_month_averages, id: false do |t|
      t.references :region, index: true, foreign_key: true, null: false
      t.references :eve_item, index: true, foreign_key: true, null: false
      t.column :order_count_sum, :bigint
      t.column :volume_sum, :bigint
      t.column :order_count_avg, :bigint
      t.column :volume_avg, :bigint
      t.float :low_price_avg
      t.float :avg_price_avg
      t.float :high_price_avg

      t.timestamps null: false
    end
    add_index :crest_prices_last_month_averages, [:region_id, :eve_item_id], unique: true, name: 'prices_lmavg_all_keys_index'
  end
end
