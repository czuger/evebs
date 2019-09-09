class ChangeEveMarketHistories < ActiveRecord::Migration[5.2]
  def change
		drop_view :group_eve_market_histories

		EveMarketHistory.delete_all

    rename_table :eve_market_histories, :eve_market_histories_groups

		remove_column :eve_market_histories_groups, :order_count, :bigint
		remove_column :eve_market_histories_groups, :server_date, :date

		change_column :eve_market_histories_groups, :region_id, :bigint, null: true
		change_column :eve_market_histories_groups, :eve_item_id, :bigint, null: true

		add_column :eve_market_histories_groups, :cpp_type_id, :integer, null: false
		add_column :eve_market_histories_groups, :cpp_region_id, :integer, null: false
  end
end
