class CreateEveMarketHistoryArchives < ActiveRecord::Migration[5.2]
  def change
    create_table :eve_market_history_archives do |t|
      t.integer :region_id, null: false
      t.integer :eve_item_id, null: false
      t.string :year, null: false
      t.string :month, null: false
      t.date :history_date, null: false
      t.integer :order_count
      t.bigint :volume
      t.float :low_price
      t.float :avg_price
      t.float :high_price

      t.timestamps
    end
  end
end
