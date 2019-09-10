class CreateEveMarketHistoriesGroupTmpTable < ActiveRecord::Migration[5.2]
  def change
		# That was a miss, I thought the tmp tables the Oracle way. PGSQL works differently : the table is dropped at the end of the session.
		# Far much clean :)

		# create_table :eve_market_histories_group_tmp_tables, :temporary=> true do |t|
		# 	t.integer :cpp_type_id, null: false
		# 	t.integer :cpp_region_id, null: false
		#
		# 	t.bigint :volume, null: false
		#
		# 	t.float :lowest
		# 	t.float :highest
		# 	t.float :average
		# end
		#
		# add_index :eve_market_histories_group_tmp_tables, [ :cpp_type_id, :cpp_region_id ], unique: true, name: :eve_market_histories_groups_cpp_index

		# execute 'CREATE TEMP TABLE eve_market_histories_group_tmp_tables( c INT );'

		change_column :eve_market_histories_groups, :eve_item_id, :bigint, null: false
		change_column :eve_market_histories_groups, :universe_region_id, :bigint, null: false

		remove_column :eve_market_histories_groups, :cpp_type_id, :integer
		remove_column :eve_market_histories_groups, :cpp_region_id, :integer
  end
end
