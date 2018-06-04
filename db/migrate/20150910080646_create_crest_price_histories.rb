class CreateCrestPriceHistories < ActiveRecord::Migration[4.2]
  def change
    create_table :crest_price_histories do |t|
      t.references :region, index: true, foreign_key: true, null: false
      t.references :eve_item, index: true, foreign_key: true, null: false
      t.string :day_timestamp, index: true, null: false
      t.timestamp :history_date, null: false
      t.column :order_count, :bigint
      t.column :volume, :bigint
      t.float :low_price
      t.float :avg_price
      t.float :high_price

      t.timestamps null: false
    end
    add_index :crest_price_histories, [:region_id, :eve_item_id, :day_timestamp], unique: true, name: 'price_histories_all_keys_index'
  end
end
