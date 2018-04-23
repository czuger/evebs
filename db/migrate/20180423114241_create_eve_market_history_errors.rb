class CreateEveMarketHistoryErrors < ActiveRecord::Migration[5.2]
  def change
    create_table :eve_market_history_errors do |t|
      t.integer :cpp_region_id
      t.integer :cpp_eve_item_id
      t.string :error

      t.timestamps
    end
  end
end
