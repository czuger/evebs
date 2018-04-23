class CreateEveEmptyMarketHistories < ActiveRecord::Migration[5.2]
  def change
    create_table :eve_empty_market_histories do |t|
      t.integer :cpp_region_id
      t.integer :cpp_eve_item_id

      t.timestamps
    end

    add_index :eve_empty_market_histories, [:cpp_region_id, :cpp_eve_item_id], unique: true, name: 'idx_eve_empty_market_histories'
  end
end
