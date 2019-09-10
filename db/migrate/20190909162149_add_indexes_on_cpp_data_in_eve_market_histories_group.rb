class AddIndexesOnCppDataInEveMarketHistoriesGroup < ActiveRecord::Migration[5.2]
  def change
    add_index :eve_market_histories_groups, [ :cpp_type_id, :cpp_region_id ], unique: true, name: :eve_market_histories_groups_cpp_index

		remove_index :eve_market_histories_groups, :eve_item_id

		remove_column :eve_market_histories_groups, :region_id

		add_reference :eve_market_histories_groups, :universe_region, foreign_key: true, index: false

		add_index :eve_market_histories_groups, [ :eve_item_id, :universe_region_id ], unique: true, name: :eve_market_histories_groups_synth_index
  end
end
